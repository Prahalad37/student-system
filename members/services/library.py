from datetime import date, timedelta
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from ..models import Book, LibraryTransaction, Member


class LibraryService:
    @staticmethod
    def issue_book(school_id: int, student_id: int, book_id: int, due_date: str = None) -> LibraryTransaction:
        """
        Issues a book safely. Prevents 'Negative Inventory' race conditions.
        """
        if not due_date:
            due_date = date.today() + timedelta(days=14)

        # 1. Start Transaction
        with transaction.atomic():
            # 2. Lock the Book Row (Critical Step)
            # This makes other requests WAIT until we are done checking stock.
            book = Book.objects.select_for_update().get(id=book_id, school_id=school_id)

            # 3. Double-Check Availability in DB
            if book.available_copies < 1:
                raise ValueError(f"Book '{book.title}' is out of stock!")

            student = get_object_or_404(Member, id=student_id, school_id=school_id)

            # 4. Create Transaction Record
            lib_tx = LibraryTransaction.objects.create(
                school_id=school_id,
                student=student,
                book=book,
                due_date=due_date,
                status='Issued'
            )

            # 5. Decrement Stock Safely
            book.available_copies = F('available_copies') - 1
            book.save()
            
            return lib_tx

    @staticmethod
    def return_book(school_id: int, transaction_id: int) -> LibraryTransaction:
        with transaction.atomic():
            tx = LibraryTransaction.objects.select_for_update().get(id=transaction_id, school_id=school_id)
            
            if tx.status == 'Returned':
                return tx  # Already returned, do nothing

            # Calculate Fine
            tx.status = "Returned"
            tx.return_date = date.today()
            
            # Simple fine logic: 10 Rs per day late
            if tx.return_date > tx.due_date:
                overdue_days = (tx.return_date - tx.due_date).days
                tx.fine_amount = overdue_days * 10
            
            tx.save()

            # Restock the book
            # We use F() here too so we don't accidentally reset the count
            book = tx.book
            book.available_copies = F('available_copies') + 1
            book.save()

            return tx
