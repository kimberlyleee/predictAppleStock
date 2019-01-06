from bs4 import BeautifulSoup
import urllib3
import csv
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model

class PredictStock:
    def __init__(self, u):
        self.url = u
        self.headerName = []
        self.dataList = []
        self.xData = []
        self.yData = []

    def collectHistoricalData(self):
        http = urllib3.PoolManager()
        response = http.request('GET', self.url)
        soup = BeautifulSoup(response.data, "html.parser")

        header = soup.find("thead")

        for row in header.find_all('span'):
            self.headerName.append(row.text)

        body = soup.find("tbody")
        for row in body.find_all('tr'):
            dataRow = []
            for td in row.find_all('td'):
                dataRow.append(td.text)
            self.dataList.append(dataRow)

    def csvWriter(self, fileName):
        with open(fileName, mode='w') as csvfile:
            fileWriter = csv.writer(csvfile, delimiter=',')
            fileWriter.writerow(self.headerName)

            for data in self.dataList:
                fileWriter.writerow(data)
            csvfile.close()

    def csvReader(self, fileName):
        try:
            with open(fileName, mode='r') as csvfile:
                fileReader = csv.reader(csvfile, delimiter=',')
                for row in fileReader:
                    print(row)
        except IOError:
            print("Error reading file: " + fileName)

    def csvDictWriter(self, fileName):
        with open(fileName, mode='w') as dictfile:
            writer = csv.DictWriter(dictfile, fieldnames=self.headerName)
            writer.writeheader()
            for data in self.dataList:
                if (len(data) != 7):
                    continue
                writer.writerow({'Date': data[0], 'Open': data[1],
                                 'High': data[2], 'Low': data[3],
                                 'Close*': data[4], 'Adj Close**': data[5],
                                 'Volume': data[6]})

    def csvDictReader(self, fileName):
        try:
            with open(fileName, mode='r') as dictfile:
                fileReader = csv.DictReader(dictfile, delimiter=',')
                for row in fileReader:
                    str = ','
                    sequence = (row['Date'], row['Open'], row['High'],
                                row['Low'], row['Close*'], row['Adj Close**'],
                                row['Volume'])
                    print(str.join(sequence))
        except IOError:
            print("Error reading file: " + fileName)

    def writeToDatabase(self):
        connection = sqlite3.connect('stockData.db')
        c = connection.cursor()
        c.execute("DELETE FROM stocks")
        c.execute('CREATE TABLE IF NOT EXISTS stocks (Date text, Open text, High text, Low text, Close text, AdjClose text, Volume text)')
        for data in self.dataList:
            if (len(data) != 7):
                continue
            row = "INSERT INTO stocks VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (data[0], data[1], data[2], data[3], data[4], data[5], data[6])
            c.execute(row)
        connection.commit()
        connection.close()

    def readDatabase(self):
        connection = sqlite3.connect('stockData.db')
        c = connection.cursor()
        allData = c.execute('SELECT * FROM stocks')
        for line in allData:
            print(line)
        connection.close()

    def getDataset(self):
        connection = sqlite3.connect('stockData.db')
        c = connection.cursor()
        openPrice = c.execute('SELECT Open FROM stocks')
        for line in openPrice:
            self.xData.append(line[0])
        closePrice = c.execute('SELECT Close FROM stocks')
        for line in closePrice:
            self.yData.append(line[0])
        connection.close()

    def linRegAndPlot(self):
        twoDxData = np.reshape(self.xData, (-1, 1))

        xTrain = twoDxData[:-20]
        xTest = twoDxData[-20:]

        twoDyData = np.reshape(self.yData, (-1, 1))
        yTrain = twoDyData[:-20]
        yTest = twoDyData[-20:]

        reg = linear_model.LinearRegression()
        reg.fit(xTrain, yTrain)
        regScore = reg.score(xTest, yTest)
        print(regScore)

        yPredict = reg.predict(xTest)
        print(yPredict)

        plt.scatter(xTest, yTest, color='black')
        plt.plot(xTest, yPredict, color='red', linewidth=3)

        plt.xticks()
        plt.yticks()

        plt.show()





apple = PredictStock("https://finance.yahoo.com/quote/AAPL/history?p=AAPL")
apple.collectHistoricalData()
# apple.csvDictWriter("testDict.csv")
# apple.csvDictReader("testDict.csv")
apple.writeToDatabase()
# apple.readDatabase()
apple.getDataset()
apple.linRegAndPlot()