import emoji

addfund = {
    "3k":[
        "All hail the Sovereign Ruler {name} 👑! There is {balance} Tk. in your treasury, your highness!",
        "Let's go on a tour ✈️ {name}! You have {balance} Tk. now in your fund. We could go to Hawaii 🏖️",
        "Do you know what comes to my mind when I see you {name}?\n\nThis: 💸💸💸\n\nHere's your balance Richie Rich: {balance} Tk.",
        "Are you planning on buying the whole store or what {name}? Here's your balance: {} Tk.",
        "DAMN 🤯! Your balance is my monthly salary 😭! {balance} Tk.?! What will you do with all these money {name}?"
    ],
    "2k":[
        "You can buy lots of coffee ☕ with this, {name}. Here's your balance: {balance} Tk",
        "Congratulations {name} 🎉! You added {amount} Tk. to your fund. Your current balance is {balance} Tk. Have a great day 😊!",
        "Looks like someone got their salary today 😏. Here's your balance {name}: {balance} Tk.\n\nGo buy yourself a nice hot coffee ☕"
    ],
    "1k":[
        "You ain't poor but you certainly ain't that rich {name}. You only have {balance} Tk. in your balance",
        "Hey {name}, {amount} Tk was added to your fund. Your current balance is {balance} Tk."
    ],
    "500":[
        "At least you're not completely broke {name}. You only have {balance} Tk. now in your account",
        "Well, something is better than nothing, right {name}? Here's your new balance: {balance} Tk."
    ],
    "<500":[
        "You understand it's not dollars, right? Adding a mere {amount} Tk. isn't going to help you that much {name}. Anways, here's your balance: {balance} Tk.",
        "Well, the tong isn't that far. So I guess it's okay having {balance} Tk. in your balance {name}",
        "When life gives you lemon 🍋 you gotta make lemonade 🍹. You have to do something like that with your {balance} Tk. balance {name}"
    ]
}

pay = {
    "None":[
        "So not gonna tell me what you had, huh 😒? Okay {name}, here's your balance: {balance} Tk.",
        "I hope what you bought with {bill} Tk. isn't something illegal. Here's your balance after that {name}: {balance} Tk."
    ],
    "0":[
        "Who invented the number 0 🤔?\n\n{name}'s bank balance 🤣",
        "You're almost a billionair {name} 🤯!\n\nYou're only a billion dollar short 🤣",
        "You ran out of money {name} 😨!. You're balance is 0 Tk.",
        "I guess {item} was worth going broke for. You have no money now {name} 😞"
    ],
    "<0":[
        "Damm {name}! You're like reverse Bruce Wayne.\n\nNo, you're not Batman, you're poor. Here's your balance: {balance} Tk.",
        "{item} made you broke {name}. Here's your balance: {balance} Tk.",
        "Oh you poor little {name}! You're now in debt. This is your balance after you had {item}: {balance} Tk.",
        "I know {name}, {item} is worth going broke for. Here's your balance though: {balance} Tk.",
        "Umm, do you need help cleaning those dishes {name}? Your balance is {balance} Tk."
    ],
    ">0day":[
        "Nothing better than a{n} {item} in the {daytype}. Here's your balance {name}: {balance} Tk.",
        "Good Day {name} 😊! You had a{n} {item}. Here's your balance: {balance} Tk.",
        "No one deserves {item} more than you {name}. You've earned it! You still have {balance} Tk. in your balance"
    ],
    ">0":[
        "Nothing better than a{n} {item} in the {daytype}. Here's your balance {name}: {balance} Tk.",
        "Good {daytype} {name} 😊! You had a{n} {item}. Here's your balance: {balance} Tk.",
        "No one deserves {item} more than you {name}. You've earned it! You still have {balance} Tk. in your balance"
    ]
}