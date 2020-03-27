
# Define a function to get the most recently modified file
import os

def get_newest_modified(dirpath, cutoff_date = None, newest = True):

    a = [s for s in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath, s))]

    # Don't bother if it's empty
    if len(a)==0:
        return ['']

    # Sort by date
    a.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)), reverse=True)

    # Cutoff by date if necessary
    if cutoff_date!=None:
        cutoff_date = pd.to_datetime(str(cutoff_date))
        a = [s for s in a if dt.datetime.fromtimestamp(os.path.getctime(os.path.join(dirpath, s))) >= cutoff_date]

    if newest==True:
        a = a[0]

    # A single return
    return a

# ---------------------------------------------
