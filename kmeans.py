import pandas as pd
import random
import json

# Deck class to store deck objects. Deck objects include:
# Type: Class label of deck. Used for getting accuracy of clustering
# Cards: List of card objects in the deck (maximum 30)
# One_Hot: One hot respresentation of cards in deck
class Deck:
    def __init__(self, type, cards):
        self.type = type
        self.cards = cards
        self.one_hot = []

    def __eq__(self, other):
        return self.type == other.type and set(self.cards) == set(other.cards)

# Returns the hamming distance between two one-hot lists
# Hamming distance is the number of elements in the list where the values differ
def hamming_distance(list1, list2):
    return sum(c1 != c2 for c1, c2 in zip(list1, list2))

# Creates a one-hot list representing a deck
# Example given deck [3, 4, 9]
# One-hot [0, 0, 0, 1, 1, 0, 0, 0, 0, 1]
def create_one_hot(list, card_dict):
    one_hot = [0 for _ in range(len(card_dict))]
    for card in list:
        one_hot[card] = 1
    return one_hot

# Creates a dictionary holding the one-hot centroid for each cluster
def create_centroids_one_hot_dict(centroids_dict, one_hot_centroids):
    count = 0
    for centroid in one_hot_centroids:
        centroids_dict[count] = centroid
        count += 1

# Returns the indcies of the 10 max elements of a given list in a list
def thirty_max_indicies(list):
    ten_max = []
    for i in range(30):
        max = 0
        for j in range(len(list)):
            if list[j] > max:
                max = list[j]
        ten_max.append(list.index(max))
        list[list.index(max)] = 0
        
    return ten_max

# Given a list of decks and centroids for each cluster
# Returns a dictionary of clusters with each deck being placed according
# to minimum hamming distance
def kmeans(deck_list, centroids_dict):

    clusters = {}
    for i in range(10):
        clusters[i] = []
    
    for deck in deck_list:
        min_distance = 10000
        for index, centroid in centroids_dict.items():
            ham_distance = hamming_distance(deck.one_hot, centroid)
            if ham_distance < min_distance:
                min_distance = ham_distance
                cluster = index
        clusters[cluster].append(deck)

    return clusters


def main():
    k = 10 # Given number of clusters
    df = pd.read_csv('hearthstone_decks.csv', header=0) # Read in the data

    card_dict = {} #len 350
    deck_list = [] #len 459
    card_count = 0
    # Create a list of deck objects each initalized with deck type and list of cards
    # Also create the card dictionary which gives each card a unique number
    for index, row in df.iterrows():
        card_series = row.iloc[5:35]
        deck = []
        for card in card_series:
            if isinstance(card, str):
                if card not in card_dict:
                    card_dict[card] = card_count
                    card_count += 1
                deck.append(card_dict[card])
        deck_list.append(Deck(row['type'], deck))

    # Create the one hot lists for each deck in the deck list
    for deck in deck_list:
        deck.one_hot = create_one_hot(deck.cards, card_dict)
    
    # Create 10 random centroids
    centroids = []
    for i in range(k):
        centroid = []
        for j in range(30):
            centroid.append(random.randrange(len(card_dict) - 1)) #Might need to fix this
        centroids.append(centroid)

    # Create the one hot lists for each centroid
    one_hot_centroids = []
    for centroid in centroids:
        one_hot_centroids.append(create_one_hot(centroid, card_dict))

    centroids_dict = {} # Used to associate cluster number with a centroid
    prev_clusters = {} # Used to compare if the clusters changed over a clustering round
    kmeans_loop_count = 0

    while True:

        # Update the centroid dictionary for this clustering round
        create_centroids_one_hot_dict(centroids_dict, one_hot_centroids)

        # Run the kmean algorithm and see if any clustering changed
        clusters = kmeans(deck_list, centroids_dict)
        if prev_clusters == clusters:
            break
        prev_clusters = clusters

        # Reset centroids to be more central for each cluster
        # Reset all one-hot centroids
        for i in range(len(one_hot_centroids)):
            one_hot_centroids[i].clear()
            for j in range(len(card_dict)):
                one_hot_centroids[i].append(0)
        
        # For each deck in the cluster find the top 30 most common cards
        # New centroid for this cluster will be composed of these 30 cards
        for index, cluster in clusters.items():
            for deck in cluster:
                for j, card in enumerate(deck.one_hot):
                    one_hot_centroids[index][j] += card
        for i in range(len(one_hot_centroids)):
            centroids[i] = thirty_max_indicies(one_hot_centroids[i])

        # Create one hot lists for the new centroids
        for i, centroid in enumerate(centroids):
            one_hot_centroids[i] = create_one_hot(centroid, card_dict)

        # Print an update on the clustering algorithm
        kmeans_loop_count += 1
        print("Clustering Round: " + str(kmeans_loop_count) + " complete")


    # Find the most common type of deck for each cluster and assign that as the cluster type
    cluster_types = {}
    for cluster_num, cluster in clusters.items():
        types_count = {}
        for deck in cluster:
            if deck.type in types_count:
                types_count[deck.type] += 1
            else:
                types_count[deck.type] = 1
        cluster_types[cluster_num] = max(types_count, key=types_count.get)

    # Test algorithm to see how accurate the clustering was
    correct = 0
    for cluster_num, cluster in clusters.items():
        for deck in cluster:
            if deck.type == cluster_types[cluster_num]:
                correct += 1

    print("Accuracy: " + str(correct/len(deck_list)) + "%")
            
        
        
    
    
    
    

main()