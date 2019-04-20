import os
import pickle

from handler import get_personcontest_score


def update_leaderboard(contest: int, person: str):
    """
    Updates the leaderboard for the passed contest for the rank of the person
    Pass pk for contest and email for person
    Only call this function when some submission for some problem of the contest
     has scored more than its previous submission.
    Remember to call this function whenever PersonProblemFinalScore is updated.
    Returns True if update was successfull else returns False 
    """

    os.makedirs(os.path.join('content', 'contests'), exist_ok=True)
    pickle_path = os.path.join('content', 'contests', str(contest)+'.lb')

    status, score = get_personcontest_score(person)

    if status:
        if not os.path.exists(pickle_path):
            f = open(pickle_path, 'wb')
            data = [[person, score]]
            pickle.dump(data, f)
            f.close()
            return True
        else:
            f = open(pickle_path, 'rb')
            data = pickle.load(f)
            f.close()
            f = open(pickle_path, 'wb')
            for i in range(len(data)):
                if data[i][0] == person:
                    data[i][1] = score
                    pos = i
                    break
            else:
                data.append([person, score])
                pos = len(data) - 1
            for i in range(pos, 0, -1):
                if data[i][1] > data[i-1][1]:
                    data[i], data[i-1] = data[i-1], data[i]
                else:
                    break
            pickle.dump(data, f)
            f.close()
            return True
    else:
        return False
