import sys
from SongLibrary import SongLibrary
from Graph import Graph

# class to find the shortest path
class PriorityQueue:
    def __init__(self):
        self.heapArray = [(0, 0)]
        self.currentSize = 0

    def buildHeap(self, alist):
        self.currentSize = len(alist)
        self.heapArray = [(0, 0)]
        for i in alist:
            self.heapArray.append(i)
        i = len(alist)//2

        while i > 0:
            self.percDown(i)
            i -= 1

    def percDown(self,i):
        while (i * 2) <= self.currentSize:
            mc = self.minChild(i)
            if self.heapArray[i][0] > self.heapArray[mc]:
                tmp = self.heapArray[i]
                self.heapArray[i] = self.heapArray[mc]
                self.heapArray[mc] = tmp
            i = mc

    def minChild(self, i):
        if i * 2 > self.currentSize:
            return -1
        else:
            if i * 2 + 1 > self.currentSize:
                return i * 2
            else:
                if self.heapArray[i * 2][0] < self.heapArray[i * 2 + 1][0]:
                    return i * 2
                else:
                    return i * 2 + 1

    def percUp(self, i):
        while i // 2 > 0:
            if self.heapArray[i][0] < self.heapArray[i // 2][0]:
                tmp = self.heapArray[i//2]
                self.heapArray[i//2] = self.heapArray[i]
                self.heapArray[i] = tmp
            i = i // 2

    def add(self, k):
        self.heapArray.append(k)
        self.currentSize = self.currentSize + 1
        self.percUp(self.currentSize)

    def delMin(self):
        retval = self.heapArray[1][1]
        self.heapArray[1] = self.heapArray[self.currentSize]
        self.currentSize = self.currentSize - 1
        self.heapArray.pop()
        self.percDown(1)
        return retval

    def isEmpty(self):
        if self.currentSize == 0:
            return True
        else:
            return False

    def decreaseKey(self, val, amt):
        done =False
        i = 1
        myKey = 0
        while not done and i <= self.currentSize:
            if self.heapArray[i][1] == val:
                done = True
                myKey = i
            else:
                i += 1
        if myKey > 0:
            self.heapArray[myKey] = (amt, self.heapArray[myKey][1])
            self.percUp(myKey)

    def __contains__(self, item):
        for pair in self.heapArray:
            if pair[1] == item:
                return True
        return False



class ArtistConnections:

    def __init__(self):
        self.vertList = {}
        self.numVertices = 0

    """
    Load the artist connections graph based on a given song database
    Add the edges based on the last column of the collaborative artists 

    """

    def load_graph(self, songLibarary):
        # global variable that holds the graph
        global g
        g = Graph()
        # to import the songLibrary using the SongLibrary class
        songLib = SongLibrary()
        songLib.loadLibrary(songLibarary)
        # gets the songArray from the imported class
        songLibrary = songLib.songArray

        for i in range(len(songLibrary)):
            for j in range(len(songLibrary[i].col_list)):
                if songLibrary[i].artist != songLibrary[i].col_list[j]:
                    # adds edge from artist to collaborator and vice-versa
                    g.addEdge(songLibrary[i].artist, songLibrary[i].col_list[j])
                    g.addEdge(songLibrary[i].col_list[j], songLibrary[i].artist)
            # adds the song to the attribute of the current artist
            g.getVertex(songLibrary[i].artist).songs.append(songLibrary[i].title)

        vertices = g.getVertices()
        self.numVertices = len(vertices)
        self.vertList = g.vertList
        # updates the object variables
        return self.numVertices

    """
    Return song libary information
    """

    def graph_info(self):
        return "Vertex Size: " + str(self.numVertices)

    """
    Search the information of an artist based on the artist name
    Return a tuple (the number of songs he/she wrote, the collaborative artist list)
    """
    # searches the artist in the graph using the artist_name
    def search_artist(self, artist_name):
        tempartistLst = g.getVertex(artist_name).coArtists.keys()
        artistList = []
        for x in tempartistLst:
            artistList.append(x.id)
        artistList.sort()
        # finds the number of songs that the artist has
        numSongs = len(g.getVertex(artist_name).songs)

        return numSongs, artistList

    """
    Return a list of two-hop neighbors of a given artist
    """

    def find_new_friends(self, artist_name):
        # function to find the two_hop_friends of the given artist
        artist = g.getVertex(artist_name)
        first_hop = artist.coArtists.keys()
        first_hop_list = []
        # uses set to remove duplicates
        second_hop_list = set()
        for x in first_hop:
            first_hop_list.append(x.id)
        for x in first_hop_list:
            a = g.getVertex(x).coArtists.keys()
            for y in a:
                second_hop_list.add(y.id)
        # creates a list of the second set of collaborators from the first
        for x in second_hop_list:
            if x in first_hop_list:
                second_hop_list.remove(x)
        # removes the given artist from the list
        second_hop_list.remove(artist_name)
        # converts set to list
        two_hop_friends = list(second_hop_list)
        two_hop_friends.sort()

        return two_hop_friends

    """
    Search the information of an artist based on the artist name
    """
    # function to recommend new collaborator
    def recommend_new_collaborator(self, artist_name):
        artist = ""
        numSongs = 0
        artist_obj = g.getVertex(artist_name)
        maxWeight = 0
        # initializes maximum weight for further comparisons
        for k,v in artist_obj.coArtists.items():
            for key,value in k.coArtists.items():
                if key.id != artist_name:
                    # checks if the sum of the two weights is greater than max
                    if (v + value) > maxWeight:
                        maxWeight = v + value
                        artist = key.id
                        numSongs = value
        return artist, numSongs

    # function to check for the shortest path
    def shortest_path(self, artist_name):
        path = {}
        secondLayer = []
        currantlayer = [] # array of running sum
        for k,v in g.getVertex(artist_name).coArtists.items():
            # each value is the distance from the collaborator
            path[k.id] = 1
            currantlayer.append(k.id)

        # since there is the  six degree of separation rule
        x = 2
        while x < 7:
            for layer in currantlayer:
                vertex = g.getVertex(layer)
                # makes sure that the vertex exists
                if vertex != None:
                    for y in vertex.coArtists:
                        if y.id != artist_name and path.get(y.id) is None:
                            path[y.id] = x
                            secondLayer.append(y.id)
            currantlayer =secondLayer
            # reinitializes the second layer
            secondLayer = []
            x += 1
        return path



# WRITE YOUR OWN TEST UNDER THAT IF YOU NEED
if __name__ == '__main__':
    g = Graph()
    # songLib = SongLibrary()
    # songLib.loadLibrary()
    artistGraph = ArtistConnections()
    artistGraph.load_graph("TenKsongs_proj2.csv")
    print(artistGraph.graph_info())
    print(artistGraph.search_artist("Mariah Carey"))
    print(artistGraph.find_new_friends("Mariah Carey"))
    print(artistGraph.recommend_new_collaborator("Mariah Carey"))
    print(artistGraph.shortest_path("Mariah Carey"))