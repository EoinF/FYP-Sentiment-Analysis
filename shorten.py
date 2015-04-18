import sys

def main():

    numFiles = 2
    if len(sys.argv) > 1:
        numFiles = int(sys.argv[1])
    w = 0
    with open("aggregatedData.csv", "r") as f:
        w = sum([1 for line in f])

    with open("aggregatedData.csv", "r") as f:
        linesAdded = 0
        
        #Attach the header line to all outputs
        header = f.readline()
        for i in range(numFiles):
            output = header

            for line in f:
                output += (line)
                linesAdded += 1
                if linesAdded >= (w / numFiles) * (i + 1):
                    break

            with open("output/shorterData%d.csv" % i, "w") as f2:
                f2.write(output)

if __name__ == "__main__":
    main()
