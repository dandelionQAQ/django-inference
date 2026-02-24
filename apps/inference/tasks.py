from celery import shared_task


@shared_task(bind=True, autoretry_for=(), retry_backoff=False)
def inference_task(self, history_id: int):
    """
    Celery 任务入口：只负责调用 service 的执行函数。
    """
    from .runner import run_inference_impl  # 延迟导入避免循环依赖

    run_inference_impl(history_id=history_id)
