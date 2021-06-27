package Project;

import java.util.Scanner;

class RockPaperScissors extends Game  {
	
	private static final String name = "Rock-Paper-Scissors";
	private static final Character  Rock = 'r';
	private static final Character Paper = 'p';
	private static final Character Scissors = 's';
	private int numRounds;
	private int victory;
	private int playerScore;
	private int computerScore;
	
	RockPaperScissors(User gamer) {
		this.gamer = gamer;
		playerScore = 0;
		computerScore = 0;
		playerPoints = 0;
	}
	
	String getName() {
		return name;
	}

	
	/*
	 *  ScoreLine Methods
	 */
	
	private void resetPlayerScore() {
		playerScore = 0;
	}
		
	private void resetComputerScore() {
		computerScore = 0;
	}
	
	private String scoreLine() {
		return "Score: You " +playerScore+	"; Me " +computerScore;
	}
	
	
	/*
	 *  Game Methods
	 */
	
	
	void play() {
		
		// Print Instructions
		gameIntro(getName());

		resetComputerScore();
		resetPlayerScore();
		numRounds = numberOfRounds();
		victory = (numRounds/2) + 1;
		
		System.out.println("\nBest " +victory+ " out of " 
												+numRounds+ " rounds.");
		
		// Iterate & play each round
		for (int i = 0; i < numRounds; i++) {
			rest(500);
			System.out.println("\nReady? Round " +(i+1)+ "\n");
			
			// Play a round and process the result
			if (round()) {
				System.out.println("\nYou win this round!!");
				playerScore++;
			}
			else {
				System.out.println("\nI win this round!");
				computerScore++;
			}
			// Check if somebody has won
			if (playerScore >= victory) {
				rest(500);
				System.out.println("\nDarn. You are victorius!");
				System.out.println(scoreLine());
				incrementPoints(playerScore * 100);
				if (computerScore == 0) {
					rest(500);
					System.out.println("\nClean Sweep!\nHave a bonus!");
					incrementPoints((playerScore * 100) / 4 );
				}
				break;
			}
			else if (computerScore >= victory) {
				System.out.println("\nWooop! I am victorius");
				System.out.println(scoreLine());
				break;
			}
			rest(500);
			System.out.println(scoreLine());	
			rest(1000);
		}
		
		quit();
			
	}
	
	
	private static boolean round() {
		
		boolean userWins = false;
		boolean draw;
		String userMove;
		
		do {
			draw = false;
			
			// Get Users Move
			do {
				userMove = getUserMove();
			} while(userMove.equals("abort"));
			
			System.out.println("\nReady?\n\nYou\tvs\tMe");
			rest(400);
			for (var i=1; i<=3; i++) {
				System.out.println("\t*" +i+ "*");
				rest(400);
			}
			
			// Make Computer Move
			String compMove = makeComputerMove();
	
			// Print the moves
			System.out.println(userMove+ "\tvs\t" +compMove);
			
			// Compare Moves
			if (userMove.equals("Rock")) {
				if (compMove.equals("Paper")) userWins = false;
				else if (compMove.equals("Scissors")) userWins = true;
				else if (compMove.equals("Rock")) draw = true;
			}
			else if (userMove.equals("Paper")) {
				if (compMove.equals("Paper")) draw = true;
				else if (compMove.equals("Scissors")) userWins = false;
				else if (compMove.equals("Rock")) userWins = true;
			}
			else if (userMove.equals("Scissors")) {
				if (compMove.equals("Paper")) userWins = true;
				else if (compMove.equals("Scissors")) draw = true;
				else if (compMove.equals("Rock")) userWins = false;
			}
			if (draw) System.out.println("\nDraw!\nReplay Round.");
		} while (draw); 
		
		return userWins;
	}

	
	private static String makeComputerMove() {

		// Generate a Random number
		int choice = getRandomNumber(1,3);
		// Convert Number to a move
		String move;
		switch (choice) {
		case 1: move = "Rock"; break;
		case 2: move = "Paper"; break;
		case 3: move = "Scissors"; break;
		default: move = "Error"; break;
		}
		
		if (move == "Error") {
			System.out.println("\nRandom Number Generator Error in R-P-S.");
			move = "Rock";
		}
		return move;
	}
	
	
	private static String getUserMove() {
		// TODO handle whitespace chars
		
		Scanner input = Input.consoleReader;
		Character choice = 'a';
		// Prompt for input
		rest(500);
		
//		if (input.hasNext()) input.nextLine();		// Clear the scanner
		
		System.out.println("\nEnter a move.\nR = Rock; P = Paper; S = Scissors\n");
		// Read input
		if (input.hasNext()) {
			choice = input.next().charAt(0);
		}
		// process input
		choice = Character.toLowerCase(choice);
		if (choice.equals(Rock)) {
			return "Rock";
		}
		else if (choice.equals(Paper)) {
			return "Paper";
		}
		else if (choice.equals(Scissors)) {
			return "Scissors";
		}
		else {
			System.out.println("Invalid Move!");
			return "abort";
		}

	}
	

}
