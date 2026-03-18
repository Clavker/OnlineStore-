from django.core.management.base import BaseCommand, CommandError
from django.db import models
from main.models import Product, StockMovement
import csv


class Command(BaseCommand):
    """Команда для экспорта остатков товаров в CSV или JSON"""
    help = 'Экспортирует остатки товаров в CSV файл'

    def add_arguments(self, parser):
        """Добавление аргументов командной строки"""
        parser.add_argument(
            '--output',
            type=str,
            default='product_residues.csv',
            help='Путь к выходному CSV файлу (по умолчанию: product_residues.csv)'
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Фильтр по категории (ID или название)'
        )
        parser.add_argument(
            '--min-stock',
            type=int,
            help='Минимальный остаток для фильтрации'
        )
        parser.add_argument(
            '--max-stock',
            type=int,
            help='Максимальный остаток для фильтрации'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['csv', 'json'],
            default='csv',
            help='Формат вывода (csv или json)'
        )
        parser.add_argument(
            '--include-movements',
            action='store_true',
            help='Включить в выгрузку историю движений товаров'
        )

    def handle(self, *args, **options):
        """Основная логика команды"""
        output_file = options['output']
        file_format = options['format']
        include_movements = options['include_movements']

        # Получаем все товары
        products = Product.objects.all().select_related('category')

        # Применяем фильтры
        if options['category']:
            # Проверяем, является ли аргумент числом (ID)
            if options['category'].isdigit():
                products = products.filter(
                    category_id=int(options['category'])
                )
            else:
                products = products.filter(
                    category__name__icontains=options['category']
                )

        if options['min_stock'] is not None:
            products = products.filter(stock__gte=options['min_stock'])

        if options['max_stock'] is not None:
            products = products.filter(stock__lte=options['max_stock'])

        # Проверяем, есть ли товары для выгрузки
        if not products.exists():
            self.stdout.write(
                self.style.WARNING(
                    'Нет товаров, соответствующих критериям фильтрации'
                )
            )
            return

        # Экспортируем в зависимости от формата
        if file_format == 'csv':
            self._export_csv(products, output_file, include_movements)
        elif file_format == 'json':
            self._export_json(products, output_file, include_movements)

        self.stdout.write(
            self.style.SUCCESS(
                f'Данные успешно экспортированы в {output_file}'
            )
        )

    def _export_csv(self, products, output_file, include_movements):
        """Экспорт в CSV формат"""
        try:
            with open(output_file, 'w', encoding='utf-8-sig',
                      newline='') as file:
                writer = csv.writer(file, delimiter=';')

                # Заголовки
                headers = [
                    'ID товара',
                    'Название',
                    'Категория',
                    'Цена',
                    'Текущий остаток',
                    'Общая стоимость остатка',
                    'Дата последнего изменения'
                ]

                if include_movements:
                    headers.extend([
                        'Всего приходов',
                        'Всего расходов',
                        'Последнее движение',
                        'Тип последнего движения'
                    ])

                writer.writerow(headers)

                # Данные по каждому товару
                for product in products:
                    # Получаем статистику движений, если нужно
                    if include_movements:
                        movements = StockMovement.objects.filter(
                            product=product
                        )
                        total_in = movements.filter(
                            movement_type='in'
                        ).aggregate(
                            models.Sum('quantity')
                        )['quantity__sum'] or 0
                        total_out = movements.filter(
                            movement_type__in=['out', 'sale']
                        ).aggregate(
                            models.Sum('quantity')
                        )['quantity__sum'] or 0
                        last_movement = movements.order_by(
                            '-created_at'
                        ).first()

                        last_movement_date = (
                            last_movement.created_at.strftime('%d.%m.%Y %H:%M')
                            if last_movement else ''
                        )
                        last_movement_type = (
                            last_movement.get_movement_type_display()
                            if last_movement else ''
                        )

                    row = [
                        product.id,
                        product.name,
                        product.category.name,
                        f'{product.price:.2f}'.replace('.', ','),
                        product.stock,
                        f'{product.price * product.stock:.2f}'.replace(
                            '.', ','
                        ),
                        product.updated_at.strftime(
                            '%d.%m.%Y %H:%M'
                        ) if hasattr(product, 'updated_at') else ''
                    ]

                    if include_movements:
                        row.extend([
                            total_in,
                            total_out,
                            last_movement_date,
                            last_movement_type
                        ])

                    writer.writerow(row)

        except Exception as e:
            raise CommandError(f'Ошибка при записи CSV файла: {str(e)}')

    def _export_json(self, products, output_file, include_movements):
        """Экспорт в JSON формат"""
        import json

        data = []

        for product in products:
            product_data = {
                'id': product.id,
                'name': product.name,
                'category': product.category.name,
                'price': float(product.price),
                'stock': product.stock,
                'total_value': float(product.price * product.stock),
            }

            if include_movements:
                movements = StockMovement.objects.filter(
                    product=product
                ).order_by('-created_at')
                movements_data = []

                for movement in movements[:10]:  # Последние 10 движений
                    movements_data.append({
                        'date': movement.created_at.isoformat(),
                        'type': movement.get_movement_type_display(),
                        'quantity': movement.quantity,
                        'reference': movement.reference,
                        'comment': movement.comment
                    })

                product_data['recent_movements'] = movements_data
                product_data['total_movements'] = movements.count()

            data.append(product_data)

        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
        except Exception as e:
            raise CommandError(f'Ошибка при записи JSON файла: {str(e)}')