import random 
import time 
print("Hello , I'm pyp chatbot ")  # + => contcatenation (concat)

name = input("what's your name ? ")
storyboard = int(input(f"Hello {name} , if you need to play the guess number press 1 , memory game press 2  , to exit press 3 : "))

match storyboard:
    case 1 :
        startRand = 1 
        endRand = 5
        secert_number = random.randint(startRand,endRand)
        attempts = 3
        # this loop for help user the sater the game
        for i in range(3 , 0 , -1):
            print(i)
        print("let's begain the game 🎮") 
        while True :
             
            guess = int(input(f"guess the number between {startRand} to {endRand}: "))

            if guess == secert_number :
                    print(f"Congratulation💕 {name} , you guess the right number")
                    break
            else:
                print(f"Sorry🤣 {name} , try again ")
                attempts -=1
                match attempts :
                    case 0 :
                        print(f"Game Over 🥳 , the secert number {secert_number}")
                        break
    case 2 : 
        print("Welcome to the memory game ")
        items = ["A" , "B" , "C" , "D"]
        random.shuffle(items)
        traget = random.choice(items)
        for item in items:
            print(item)
        time.sleep(2)
        print("\n" * 100 )
        answer =  int(input(f"Where is the {traget} ? "))
        if traget == items[answer-1]:
            print("correct 🎉")
        else: 
            print("Sorry 😂")
    case 3 : 
        print("open the game if you need")
    case _ : 
        print("sorry the number 1 or 2 ")    

