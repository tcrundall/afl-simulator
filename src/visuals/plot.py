import matplotlib.pyplot as plt  # type: ignore
from IPython import display
from typing import List

plt.ion()


def plot(scores: List[int], mean_scores: List[float]) -> None:
    display.clear_output(wait=True)  # type: ignore
    display.display(plt.gcf())  # type: ignore
    plt.clf()
    plt.title("Training..")
    plt.xlabel("Number of Games")
    plt.ylabel("Score")
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores) - 1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores) - 1, mean_scores[-1], str(mean_scores[-1]))
