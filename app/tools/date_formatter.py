from datetime import datetime

def get_deletionTime(delete_sched):
    if delete_sched:
        now = datetime.now().date() 
        diff = delete_sched - now  # Calculate the difference between the future date and now
        
        # If the difference is negative, it means the deletion time has passed
        if diff.days < 0:
            return "Deletion time has passed."
        
        # Format the time difference as a string indicating days left
        if diff.days > 0:
            time_str = f"{diff.days} days left" 
            return time_str
    else:
        return "Deletion schedule not provided."

def sched_accountDeletion(delete_sched):
    if delete_sched:
        now = datetime.now().date() 
        diff = delete_sched - now  # Calculate the difference between the future date and now
        
        # If the difference is negative, it means the deletion time has passed
        if diff.days < 0:
            return "Deletion time has passed."
        
        # Format the time difference as a string indicating days left
        if diff.days > 0:
            time_str = f"{diff.days} days left" 
            return time_str
    else:
        return "Deletion schedule not provided."
    
def onlineStatus(last_online):
    if not last_online:
        return None
    else:
        # Calculate the difference between the current time and the last online time
        now = datetime.now()
        diff = now - last_online 
        # Break down the difference into weeks, days, hours, minutes, and seconds
        weeks, days = divmod(diff.days, 7)
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Format the time difference based on the largest non-zero time unit
        if weeks > 0:
            if days > 0:
                return f"Offline {weeks} weeks and {days} days ago"
            else:
                return f"Offline {weeks} weeks ago"
        elif days > 0:
            return f"Offline {days} days ago"
        elif hours > 0:
            return f"Offline {hours} hours and {minutes} minutes ago"
        elif minutes > 0:
            return f"Offline {minutes} minutes ago"
        else:
            return f"Offline {seconds} seconds ago"
        