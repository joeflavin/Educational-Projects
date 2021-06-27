package Project;

import java.util.Scanner;

abstract class Game {
	
	protected String name;
	protected User gamer;
	protected int playerPoints;
	
	
	Game() {}
	
	Game(User gamer) {
		this.gamer = gamer;
	}
	
	abstract void play();
	
	abstract String getName();
	
	// Game Points - points scored playing this game instance
	int getPoints() {
		return playerPoints;
	}
		
	void incrementPoints(int points) {
		System.out.println("\nAdding " +points+ " points!");
		playerPoints += points;
	}

	// Add game points to player's session points
	void awardPoints() {
		System.out.println("\nYou have scored " +getPoints()+ " points.");
		gamer.incrementPoints(getPoints());
		rest(500);
		System.out.println("\nYour points for this gaming session are " 
														+ gamer.getPoints());
	}
	
	// Game End Logic
	void quit() {
		awardPoints();
		if (playAgain()) {
			Menu.gameMenu(gamer);
		}
		else {
			gamer.endSession();
			Menu.welcome();
		}
	}
	
	
	/*
	 *  Static methods to be used by games
	 */
		
	// Game Intro Message
	static void gameIntro(String name) {
		System.out.println("\nWelcome to " + name);
	}
		
	// Determine number of rounds
	static int numberOfRounds() {
		int choice = 0;
		Scanner input = Input.consoleReader;
		
		System.out.println("\nHow many rounds would you like? 3,5,7?");
		if (input.hasNextInt()) {
			choice = input.nextInt();	// Set Choice
		}
		else {
			input.next();			// Consume invalid input
		}
		
		while (!(choice == 3 || choice == 5 || choice == 7)) {
			System.out.print("Please enter a valid numerical option: ");
			if (input.hasNextInt()) {
				choice = input.nextInt();
			}
			else {
				input.next();	// Consume invalid input
			}
		}
		
//		System.out.println("\nYou have chosen " +choice+ " rounds.");
		return choice;
	}
	
	// Play again ?
	static boolean playAgain() {
		boolean choice = false;
		String message = "\nPlay Another Game?\n 1. Yes.\n 2. No";
		
		int numericalChoice = Input.getOption(1,2, message);
		
		switch (numericalChoice) {
			case 1: choice = true; break;
			case 2: choice = false; break;
			default: break;
		}
		return choice;
	}

	
	/*
	 * Static methods to be used by games (and possibly other objects)
	 */
	
	// Generate a random number between min & max inclusive
	static int getRandomNumber(int min, int max) {
		return (int) ((Math.random() * (max-min+1)) + min);
	}
	

	/* Sleep for milliseconds; slows progress to improve usability
	 * 
	 * Catches & ignores InterruptedException.
	 * As only used to delay printing to screen should be ok if not
	 * best practice
	 * */
	static void rest(int milliseconds) {
		try { Thread.sleep(milliseconds); } catch (InterruptedException e) {}
	}

}
