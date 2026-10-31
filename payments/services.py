import uuid
from decimal import Decimal


class PaymentGatewayService:
    """
    Payment Gateway Interface and Mock Provider.
    Structured to seamlessly drop in Razorpay SDK (razorpay.Client) in production.
    """

    @classmethod
    def create_order(cls, amount, currency='INR', receipt=None):
        """
        Creates an order with the gateway.
        In Razorpay, this calls client.order.create({amount: amount*100, currency: currency, receipt: receipt}).
        """
        order_id = f"order_{uuid.uuid4().hex[:14]}"
        return {
            'id': order_id,
            'amount': float(amount),
            'currency': currency,
            'receipt': receipt or f"rcpt_{uuid.uuid4().hex[:8]}",
            'status': 'created',
        }

    @classmethod
    def verify_payment_signature(cls, order_id, payment_id, signature):
        """
        Verifies payment signature.
        In Razorpay, this uses client.utility.verify_payment_signature(params_dict).
        """
        if order_id and payment_id:
            return True
        return False

    @classmethod
    def capture_payment(cls, booking, payment_method, amount):
        """
        Processes simulated payment transaction and creates payment ledger record.
        """
        from .models import Payment

        order = cls.create_order(amount=amount, receipt=booking.booking_id)
        payment_id = f"pay_{uuid.uuid4().hex[:14]}"
        txn_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"

        payment = Payment.objects.create(
            booking=booking,
            transaction_id=txn_id,
            amount=amount,
            payment_method=payment_method,
            status='SUCCESS',
            gateway_order_id=order['id'],
            gateway_payment_id=payment_id,
            gateway_signature=f"sig_{uuid.uuid4().hex[:20]}",
            response_payload=f'{{"status":"captured","method":"{payment_method}","order_id":"{order["id"]}","payment_id":"{payment_id}"}}'
        )
        return payment
