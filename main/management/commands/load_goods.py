from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from main.models import Product, Category, StockMovement
import csv
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Загружает товары из CSV файла и создает движения остатков'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str,
                            help='Путь к CSV файлу с товарами')
        parser.add_argument(
            '--movement-type',
            type=str,
            choices=['in', 'adjustment'],
            default='in',
            help='Тип движения для создаваемых записей (по умолчанию: in)'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='ID пользователя, от имени которого создаются движения'
        )

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        movement_type = options['movement_type']
        user_id = options.get('user_id')

        # Проверяем существование файла
        if not os.path.exists(csv_file_path):
            raise CommandError(f'Файл {csv_file_path} не найден')

        # Получаем пользователя, если указан
        user = None
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f'Пользователь с ID {user_id} не найден, движения будут без автора')
                )

        # Читаем CSV файл
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                # Проверяем наличие необходимых колонок
                required_columns = ['name', 'price', 'stock', 'category']
                if not all(
                        col in reader.fieldnames for col in required_columns):
                    raise CommandError(
                        f'CSV файл должен содержать колонки: {", ".join(required_columns)}'
                    )

                created_count = 0
                updated_count = 0
                movement_count = 0

                for row in reader:
                    # Получаем или создаем категорию
                    category_name = row['category'].strip()
                    category, _ = Category.objects.get_or_create(
                        name=category_name
                    )

                    # Получаем или создаем товар
                    product, created = Product.objects.get_or_create(
                        name=row['name'].strip(),
                        defaults={
                            'description': row.get('description', ''),
                            'price': float(row['price']),
                            'stock': 0,
                            # временно 0, потом обновим через движение
                            'category': category
                        }
                    )

                    if created:
                        created_count += 1
                        action = 'создан'
                    else:
                        updated_count += 1
                        action = 'обновлен'

                    # Создаем движение остатков
                    old_stock = product.stock
                    new_stock = int(row['stock'])

                    if movement_type == 'adjustment':
                        # Для корректировки просто устанавливаем новое значение
                        quantity_diff = new_stock - old_stock
                    else:
                        # Для прихода добавляем к существующему
                        quantity_diff = new_stock

                    if quantity_diff != 0:
                        StockMovement.objects.create(
                            product=product,
                            quantity=abs(quantity_diff),
                            movement_type=movement_type if quantity_diff > 0 else 'out',
                            reference=f'Загрузка из CSV: {os.path.basename(csv_file_path)}',
                            created_by=user,
                            comment=f'Старый остаток: {old_stock}, новый: {new_stock}'
                        )
                        movement_count += 1

                        # Обновляем остаток товара
                        if movement_type == 'adjustment':
                            product.stock = new_stock
                        else:
                            product.stock = old_stock + new_stock
                        product.save()

                    self.stdout.write(
                        f'{action} товар: {product.name} (категория: {category.name})'
                    )

                # Выводим итоги
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nГотово!\n'
                        f'Создано товаров: {created_count}\n'
                        f'Обновлено товаров: {updated_count}\n'
                        f'Создано движений остатков: {movement_count}'
                    )
                )

        except Exception as e:
            raise CommandError(f'Ошибка при обработке файла: {str(e)}')
