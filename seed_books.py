# -*- coding: utf-8 -*-
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Book_Management.settings')
django.setup()

from django.db import connection
from Book_Management.models import Books

Books.objects.all().delete()
try:
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='Book_Management_books'")
except Exception:
    pass

data = [
    {
        "title": "พื้นฐานการเขียนโปรแกรม",
        "author": "สมชาย ใจดี",
        "price": 250.00,
        "stock": 10,
        "category": "Programming"
    },
    {
        "title": "เรียนรู้ IoT ด้วย ESP32",
        "author": "วิชัย เทคโน",
        "price": 320.00,
        "stock": 5,
        "category": "IoT"
    },
    {
        "title": "Data Science เบื้องต้น",
        "author": "สมหญิง ข้อมูล",
        "price": 450.00,
        "stock": 8,
        "category": "Data Science"
    }
]

Books.objects.all().delete()

for item in data:
    book = Books.objects.create(**item)

print(f"Total books in database: {Books.objects.count()}")
for b in Books.objects.all():
    print(f"[{b.id}] {b.title} | {b.author} | {b.price} | {b.stock} | {b.category} | Created: {b.created_at} | Updated: {b.updated_at}")
