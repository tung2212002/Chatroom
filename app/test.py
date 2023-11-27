import asyncio
import websockets


fake_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InR1bmdvbmciLCJ1c2VyX2lkIjozLCJpYXQiOjE3MDA3OTg0NzQsImV4cCI6MTcwMDgwMjA3NH0.6TCPdQkcnsS59PmQ0W6_5E1tlLDln66l1cgAmKmdEqU"

# check max connections by opening multiple connections
async def check_max_connections_async():
    number_of_connections = 0
    try:
        while True:
            uri = "ws://localhost:8000/ws/connect"
            websocket = await websockets.connect(uri)
            number_of_connections += 1

    except Exception as e:
        print(e)
        print(number_of_connections)

async def check_single_connection_async(i):
    uri = "ws://localhost:8000/ws/checkconnection/"

    try:
        async with websockets.connect(uri + str(i)) as websocket:
            return True
    except Exception as e:
        return False

async def check_max_connections_async1(number_of_connections):
    uri = "ws://localhost:8000/ws/checkconnection/"
    try:
        tasks = [check_single_connection_async(i) for i in range(number_of_connections)]
        results = await asyncio.gather(*tasks)

    except Exception as e:
        print(e)


# check max connections by open and close connections
async def check_single_connect_close_async(i):
    uri = "ws://localhost:8000/ws/checkconnection/"
    try:
        async with websockets.connect(uri + str(i)) as websocket:
            await websocket.close()
    except Exception as e:
        return False

async def check_max_connections_async2(number_of_connections):
# async def check_max_connections_async2():
    try:
        number_of_connections_per = 400
        # while True:
        #     uri = "ws://localhost:8000/ws/checkconnection"
        #     websocket = await websockets.connect(uri)
        #     number_of_connections += 1
        #     await websocket.close()
        for x in range(int(number_of_connections/number_of_connections_per)):

            tasks = [check_single_connect_close_async(i) for i in range(x*number_of_connections_per, (x+1)*number_of_connections_per)]
            results = await asyncio.gather(*tasks)
        

    except Exception as e:
        print(e)


if __name__ == "__main__":
    while True:
        print("choice 0: exit")
        print("choice .: check max connections by opening multiple connections 1")
        print("choice 1: check max connections by opening multiple connections")
        print("choice 1.1: check max connections by opening multiple connections with locust")
        print("choice 2: check max connections by open and close connections")
        choice = input("Enter your choice: ")
        if choice == "1":
            asyncio.run(check_max_connections_async())


        elif choice == "2":
            # asyncio.run(check_max_connections_async2())

            print("Input number of connections: ")
            number_of_connections = int(input())
            asyncio.run(check_max_connections_async2(number_of_connections))
        elif choice == ".":
            print("Input number of connections: ")
            number_of_connections = int(input())
            asyncio.run(check_max_connections_async1(number_of_connections))
        elif choice == "0":
            break
        else:
            print("Again")
            continue




