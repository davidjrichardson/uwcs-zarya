from django.contrib import admin

from .models import EventType, SeatingRoom


@admin.register(SeatingRoom)
class SeatingRoomAdmin(admin.ModelAdmin):
    fields = ('name', 'tables_raw', 'tables_pretty', 'max_capacity')
    readonly_fields = ('max_capacity', 'tables_pretty')
    list_display = ('name', 'number_of_tables', 'capacity')
    search_fields = ('name', 'capacity')

    def capacity(self, obj):
        return obj.max_capacity

    def number_of_tables(self, obj):
        return len(obj.tables.keys())


admin.site.register(EventType)
