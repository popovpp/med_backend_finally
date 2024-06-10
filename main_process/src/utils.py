from sqlalchemy.future import select as async_select
from sqlalchemy import func

from core.sa_tables.main_process import (PayKeeperPaymentDataTable, UserPaymentTable, UserPurchaseTable, ServiceTable)

from core.config.db import get_session
from core.config.settings import SUBSCRIBE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE


async def getting_subscribe_paid_sum(patient_id, policy_id):

    async with get_session() as s:

        subscribe_paid_sum = (await s.execute(async_select(
            func.sum(PayKeeperPaymentDataTable.pay_amount)
        ).outerjoin(
            UserPaymentTable,
            UserPaymentTable.id == PayKeeperPaymentDataTable.user_payment_id
        ).outerjoin(
            UserPurchaseTable,
            UserPurchaseTable.user_payment_id == UserPaymentTable.id
        ).filter(
            PayKeeperPaymentDataTable.user_payment.has(UserPaymentTable.policy_id == policy_id),
            PayKeeperPaymentDataTable.user_payment.has(UserPaymentTable.user_id == patient_id),
            UserPurchaseTable.service.has(
                ServiceTable.client_service_code == SUBSCRIBE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE
            )
        ))).scalar()

        if not subscribe_paid_sum:
            subscribe_paid_sum = 0

    return subscribe_paid_sum
