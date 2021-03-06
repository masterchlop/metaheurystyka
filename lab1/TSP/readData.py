
import time
import tsplib95
start_time = time.time()
import sys
from scipy.spatial.distance import pdist, squareform
import numpy as np
np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)

class ReadData():
    def __init__(self, filename,matrixplik = False):
        if  matrixplik == False:
            self.sufix = ".tsp"
            self.filename = filename
            self.name = filename[:-4]
            self.size = self.getSize()
            self.EdgeWeightType = self.getEdgeWeightType()

            self.format_ = self.getFormat() # for EXPLICIT data only
            self.dis_mat = self.GetDistanceMat()

            self.time_to_read = 0
        else:
            problem = tsplib95.load(filename)
            self.sufix = ".atsp"
            self.filename = filename
            self.EdgeWeightType = 'FULL_MATRIX'
            self.name = filename[:-4]
            self.dis_mat = self.getMatrix(problem)
            self.size = self.getSize()


    def getMatrix(self,problem):
        dimension = len(list(problem.get_nodes()))
        edges = list(problem.get_edges())

        mat = [[None for _ in range(dimension)] for _ in range(dimension)]

        for edge in edges:
            mat[edge[0] - 1][edge[1] - 1] = problem.get_weight(*edge)

        return mat

    def getFormat(self):
        """

        :return: format of matrix or None(if it isn't matrix)
        """
        format = "None"
        try:
            with open(f'{self.name}{self.sufix}') as data:
                datalist = data.read().split()
                for ind, elem in enumerate(datalist):
                    if elem == "EDGE_WEIGHT_FORMAT:":
                        format = datalist[ind + 1]
                        break
                    elif elem == "EDGE_WEIGHT_FORMAT":
                        format = datalist[ind + 2]
                        break
            return format

        except :
            try:
                self.name = self.filename[:-5]
                with open(f'{self.name}{self.sufix}') as data:

                    datalist = data.read().split()
                    for ind, elem in enumerate(datalist):
                        if elem == "EDGE_WEIGHT_FORMAT:":
                            format = datalist[ind + 1]
                            break
                        elif elem == "EDGE_WEIGHT_FORMAT":
                            format = datalist[ind + 2]
                            break

                    return format
            except:
                print("wrong input data")
                sys.exit(1)



    def getEdgeWeightType(self):
        """
            return type of data(EUC_2d or EXPLICIT)

        """

        EdgeType = "None"
        try:
            with open(f'{self.name}{self.sufix}') as data:
                datalist = data.read().split()
                for ind, elem in enumerate(datalist):
                    if elem == "EDGE_WEIGHT_TYPE:":
                        EdgeType = datalist[ind + 1]
                        # print(EdgeType)
                        break
                    elif elem == "EDGE_WEIGHT_TYPE":
                        EdgeType = datalist[ind + 2]
                        # print(EdgeType)
                        break
            return EdgeType
        except:
            try:
                self.name = self.filename[:-5]
                with open(f'{self.name}{self.sufix}') as data:
                    datalist = data.read().split()
                    for ind, elem in enumerate(datalist):
                        if elem == "EDGE_WEIGHT_TYPE:":
                            EdgeType = datalist[ind + 1]
                            # print(EdgeType)
                            break
                        elif elem == "EDGE_WEIGHT_TYPE":
                            EdgeType = datalist[ind + 2]
                            # print(EdgeType)
                            break
                return EdgeType
            except:
                print("wrong input file")
                sys.exit(1)



    def getSize(self):
        """
        Return size of instances (i.e. Number of
        cities)

        """
        size = 0
        try:

            with open(f'{self.name}{self.sufix}') as data:
                datalist = data.read().split()
                for ind, elem in enumerate(datalist):
                    if elem == "DIMENSION:":
                        size = datalist[ind + 1]
                        # print(size)
                        break
                    elif elem == "DIMENSION":
                        size = datalist[ind + 2]
                        # print(size)
                        break
            return int(size)
        except IOError:
            try:
                self.name = self.filename[:-5]
                self.sufix =".atsp"
                with open(f'{self.name}{self.sufix}') as data:

                    datalist = data.read().split()

                    for ind, elem in enumerate(datalist):
                        if elem == "DIMENSION:":
                            size = datalist[ind + 1]
                            break
                        elif elem == "DIMENSION":
                            size = datalist[ind + 2]
                            break

                return int(size)
            except:
                print("file not found1")
                sys.exit(1)


    def read_Data(self):
        """

        :return: list of cities  [city, x, y]
        """
        with open(f'{self.name}{self.sufix}') as data:
            cities = []
            Isdata = True
            while (Isdata):
                line = data.readline().split()
                if len(line) <= 0:
                    break
                tempcity = []
                for i, elem in enumerate(line):
                    try:
                        temp = float(elem)
                        tempcity.append(temp)
                    except ValueError:
                        break
                if len(tempcity) > 0:

                    if self.sufix == ".atsp":

                        line = data.readline().split()
                        for i, elem in enumerate(line):
                            try:
                                temp = float(elem)
                                tempcity.append(temp)
                            except ValueError:
                                break
                    if len(tempcity) > 0:
                        cities.append(np.array(tempcity,dtype=int))



        return np.array(cities)

    def GetDistanceMat(self):
        """

        :return:  list of vectors with distances to other cities
        """
        if self.EdgeWeightType == "EXPLICIT":
            DistanceMat = self.getMat()
            self.time_to_read = time.time() - start_time
            return DistanceMat
        elif self.EdgeWeightType == "EUC_2D":
            DistanceMat = self.EuclidDist()
            self.time_to_read = time.time() - start_time
            return DistanceMat

        else:
            return None

    def EuclidDist(self):
        """

        :return: list of vectors with distances to other cities (function for Euclides data type)
        """
        cities = self.read_Data()
        # DistanceDict = {}
        A = cities[:, 1:3]
        DistanceMat = np.round(squareform(pdist(A)))

        return DistanceMat.astype(int)


    def getMat(self):
        """

        :return: list of vectors with distances to other cities (function for matrix data type)
        """
        DataFormat = self.getFormat()
        if DataFormat == "FULL_MATRIX":
            cities = self.read_Data()

            DistanceMat = cities[:self.size]

            # print(DistanceMat[0])
            # print(type(DistanceMat[0][0]))

            return DistanceMat

        elif DataFormat == "LOWER_DIAG_ROW":

            with open(f'{self.name}{self.sufix}') as file:
                indicator = False
                data = file.read().split()
                templist = []
                cities = []
                for elem in data:
                    if elem == "EDGE_WEIGHT_SECTION":
                        indicator = True
                        continue
                    if indicator:
                        try:
                            it = float(elem)
                            templist.append(it)
                        except:
                            break
                        if it == 0:
                            cities.append(templist)

                            templist = []


                DistanceMat = np.zeros((self.size, self.size))
                for i in range(self.size):
                    temp = []
                    l = len(cities[i])
                    for j in range(self.size):
                        if j <= (l - 1):
                            temp.append(cities[i][j])
                        else:
                            temp.append(cities[j][i])
                    DistanceMat[i] = temp

                return DistanceMat.astype(int)

        else:
            sys.exit("No Format Match for EXPLICIT data")
