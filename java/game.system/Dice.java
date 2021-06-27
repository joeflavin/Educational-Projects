package Project;

import java.util.Scanner;

class Dice extends Game {
	
	private static final String name = "Bank Craps";
	private int playerPurse;
	private int playerBet;
	
	Dice(User gamer) {
		this.gamer = gamer;
		playerPurse = 100;
		if (gamer instanceof VIP) playerPurse += 20;
	}
	
	String getName() {
		return name;
	}
	
	private int getPlayerPurse() {
		return playerPurse;
	}
	
	private void incrementPlayerPurse(int amount) {
		if (amount > 0) { 
			playerPurse += amount;
			System.out.println("\nAdding " +amount+ " to your purse...");
			System.out.println("Your purse is now " +getPlayerPurse()+ ".");
		}
	}
	
	private void decrementPlayerPurse(int amount) {
		if (amount > 0) playerPurse -= amount;
	}
	
	private int getPlayerBet() {
		return playerBet;
	}
	
	private void setPlayerBet(int amount) {
		if (amount > 0) playerBet = amount;
	}
	
	
	/*
	 * Game Methods
	 */
	
	void play() {
		
		int initialPurse = getPlayerPurse();
		
		String instructions = "\n****************Instructions**************************"
							+"\nBet on the roll of 2 dice." 
								+"\n7 or 11 wins. 2, 3 or 12 Loses."
									+ "\nAnything else establishes a Point."
										+ "\nRoll the Point again to win."
											+ " But roll a 7 you lose!"
							+"\n*****************************************************";
		
		String message = "\nWould you like to play another round?\n1. Yes\n2. No";
		
		gameIntro(getName());
		System.out.println(instructions);
		
		do {
			round();
			// Ask to quit
			int option = Input.getOption(1, 2, message);
			switch (option) {
				case 1: break;
				case 2: int winnings = getPlayerPurse() - initialPurse;
						if (winnings > 0) incrementPoints(winnings);
						else incrementPoints(0);
						quit();
						break;
				default: break;
			}			

		} while (getPlayerPurse() > 0);
		
		System.out.println("\nEmpty Purse. Time to leave...");
		quit();
	}
	
	
	private void round() {
		int bet = takeBet();
		
		while (!makeBet(bet)) {
			bet = takeBet();
		}
		
		rest(600);
		
		System.out.println("\nRolling Dice....");
		for (int i=0; i<3; i++) {
			rest(300);
			System.out.println("\t\t::");
		}

		int[] roll = rollDice();
		int total = roll[0] + roll[1];
		System.out.println(displayRoll(roll));
		rest(600);
		
		if (total == 7 || total == 11) {
			System.out.println("\nWe have a winner!!");
			rest(600);
			incrementPlayerPurse(bet*2);
		}
		else if (total == 2 || total == 3 || total == 12) {
			
			if (roll[0] == 1 && roll[1] == 1) {
				System.out.println("\nSNAKE EYES!");
			}
 			
			System.out.println("\nYou lose!!");
		}
		else {
			int point = total;
			int pointTotal;
			rest(600);
			System.out.println("\nPoint established: " +point);
			System.out.println("\nRoll " +point+ " to win; 7 loses.");
			rest(1000);

			do {
				rest(600);
				
				System.out.println("\nRolling Dice....");
				for (int i=0; i<3; i++) {
					rest(300);
					System.out.println("\t\t::");
				}
				
				int[] pointRoll = rollDice();
				pointTotal = pointRoll[0] + pointRoll[1];
				System.out.println(displayRoll(pointRoll));
				
				rest(600);
				
			}while (pointTotal != point && pointTotal != 7);
			
			if (pointTotal == point) {
				System.out.println("\nWe have a winner!!");
				rest(400);
				incrementPlayerPurse(bet*2);
			}
			else if (pointTotal == 7) {
				System.out.println("\nYou lose!!");
			}
			else {
				System.out.println("\nSome dicey error has occurred!?!");
			}
			
		}
		
	}
	
	
	private int takeBet() {
		int choice = -1;
		String instructions = "\nYou have " +getPlayerPurse()+ " credits."
								+ "\n Enter a bet: ";
		Scanner input = Input.consoleReader; 
		
		System.out.println(instructions);
		
		if (input.hasNextInt()) {
			choice = input.nextInt();	// set choice
		}
		else {
			input.next();		// Consume invalid input
		}
		
		while (choice < 0) {
			System.out.println("\nPlease enter a valid bet: ");
			if (input.hasNextInt()) {
				choice = input.nextInt();
			}
			else {
				input.next();
			}
		}
		
		return choice;
	}
	
	
	private boolean makeBet(int bet) {
		
		if (getPlayerPurse() < bet) {
			System.out.println("\nYou don't have sufficient credits for that.");
			return false;
		}
		else {
			decrementPlayerPurse(bet);
			setPlayerBet(bet);
			System.out.println("\nYou have bet " +getPlayerBet()+ " credits.");
			return true;
		}
	}
	
	
	private static int[] rollDice() {
		int[] results = new int[2];
		results[0] = getRandomNumber(1, 6);
		results[1] = getRandomNumber(1, 6);
		return results;
	}
	
	
	private static String displayRoll(int[] roll) {
		int total = roll[0] + roll[1];
		return "\n\t\t" +roll[0]+ "\n\t\t   " +roll[1]+ "\n\n\t\tTotal: " +total;
		
	}
	
	

	 

}
