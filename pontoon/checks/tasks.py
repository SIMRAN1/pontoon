import logging
import time

from celery import shared_task

from django.db import transaction

from pontoon.base.models import Translation
from pontoon.checks.utils import bulk_run_checks

log = logging.getLogger(__name__)


@shared_task(bind=True)
def check_translations(self, translations_pks):
    """
    Run checks on translations
    :arg list[int] translations_pks: list of primary keys for translations that should be processed
    """
    start_time = time.time()

    with transaction.atomic():
        translations = (
            Translation.object
            .for_checks()
            .filter(pk__in=translations_pks)
        )

        warnings, errors = bulk_run_checks(translations)

        log.info("Task[{}]: Processed items: {}, Warnings({}) Errors({}) in {}".format(
            self.request.id,
            len(translations),
            len(warnings),
            len(errors),
            time.time() - start_time
        ))
