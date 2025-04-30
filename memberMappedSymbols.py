from dbConfig import conn

cursor = conn.cursor()

def getSymbols():

    cursor.execute("SELECT symbol FROM symbol_dimension_table")
    symData = cursor.fetchall()
    symbols = [data[0] for data in symData]

    #print(symbols)
    return symbols


def getMember():

    cursor.execute("SELECT member_id FROM member_dimension")
    memData = cursor.fetchall()
    memberIds = [data[0] for data in memData]

    #print(memberIds)
    return memberIds


def mapSymbolTOMember(symbols, members):
    # print(symbols,'\n',members)

    memberSymbol = {}
    cnt = 0
    for mem in members:
        lst = []
        for i in range(0,20):
            lst.append(symbols[cnt+i])
        cnt += i + 1
        memberSymbol[mem]=lst


    print(memberSymbol)

    for mem,sym in memberSymbol.items():
        for s in sym:
            print(mem,s)
            cursor.execute("INSERT INTO member_symbol_assignment VALUES(%s,%s)",(mem,s))
    conn.commit()

    cursor.close()
    conn.close()




def main():
    pass
    symbols = getSymbols()
    members = getMember()
    mapSymbolTOMember(symbols, members)


if __name__ =="__main__":
    main()

