import json

def main():
    with open("addressMatches.json") as f:
        matches = json.loads(f.read())

    output = "threadID, date, price"
    for thread_id in matches:
        date, address, price = matches[thread_id][0].split(":")

        #
        #Output the line of data (excluding the address)
        #
        price = price.replace(",", "")
        output += "\n%s,%s,%s" % (thread_id, date, price)

    with open("priceValues.csv", "w") as f:
        f.write(output)

if __name__ == "__main__":
    main()
