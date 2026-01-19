from django.apps import AppConfig


class ExpenseReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'expense_reports'
    
    def ready(self):
        """
        Import signals when the app is ready.
        This ensures signal handlers are registered.
        """
        import expense_reports.signals