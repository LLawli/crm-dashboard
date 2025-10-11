from datetime import datetime, timedelta

def period_handler(period: str, date_from: str | None = None, date_to: str | None = None) -> tuple[datetime, datetime, datetime, datetime]:
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    try:
        if period == "yesterday":
            init = today - timedelta(days=1)
            end = init.replace(hour=23, minute=59, second=59, microsecond=999999)
            prev_init = init - timedelta(days=1)
            prev_end = end - timedelta(days=1)
            return init, end, prev_init, prev_end

        elif period == "week":
            init = today - timedelta(days=((today.weekday() + 1) % 7))
            init = init.replace(hour=0, minute=0, second=0, microsecond=0)
            end = datetime.now()
            prev_init = init - timedelta(days=7)
            prev_end = init - timedelta(microseconds=1)
            return init, end, prev_init, prev_end

        elif period == "month":
            init = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = today
            prev_end = init - timedelta(microseconds=1)
            prev_init = prev_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return init, end, prev_init, prev_end

        elif period == "custom" and date_from and date_to:
            try:
                date_from_datetime = datetime.strptime(date_from, "%d/%m/%Y")
                date_to_datetime = datetime.strptime(date_to, "%d/%m/%Y")
            except Exception:
                raise  

            if date_from_datetime > date_to_datetime:
                date_to_datetime = date_from_datetime + timedelta(days=1) 

            init = date_from_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            end = date_to_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
            delta = end - init
            prev_end = init - timedelta(microseconds=1)
            prev_init = prev_end - delta
            return init, end, prev_init, prev_end

    except Exception:
        pass  


    init = today
    end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    prev_end = init - timedelta(microseconds=1)
    prev_init = init - timedelta(days=1)
    return init, end, prev_init, prev_end
