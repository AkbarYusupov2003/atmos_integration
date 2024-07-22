from django.contrib.postgres.fields import JSONField
from django.db import transaction

from payment import models


class TransactionManager:

    @staticmethod
    def create_instance(data: dict):
        try:
            with transaction.atomic():
                instance = models.Transaction.objects.create(**data)
                return instance
        except Exception as e:
            print(f"An error occurred during creation: {e}")
            return None

    @staticmethod
    def update_instance(instance: models.Transaction, data: dict):
        try:
            with transaction.atomic():
                for key, value in data.items():
                    if isinstance(instance._meta.get_field(key), JSONField):
                        existing_data = getattr(instance, key, {})
                        if isinstance(existing_data, dict):
                            existing_data.update(value)
                        else:
                            existing_data = value
                        setattr(instance, key, existing_data)
                    else:
                        setattr(instance, key, value)
                instance.save()
                return instance
        except Exception as e:
            print(f"An error occurred during update: {e}")
            return None

    @staticmethod
    def delete_instance(instance: models.Transaction):
        try:
            with transaction.atomic():
                instance.delete()
                return True
        except Exception as e:
            print(f"An error occurred during deletion: {e}")
            return False
