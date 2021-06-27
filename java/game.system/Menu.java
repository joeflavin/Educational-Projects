package Project;

import java.util.Collections;
import java.util.Scanner;

class Menu {
	
	private static boolean firstTime = true; 
		
	static void welcome() {
			
		String message = "\n*******************************\nWelcome to the GAME SYSTEM"
							+ "\n*******************************\n";
		String options =  "\n***********Main Menu***********"
							+ "\nPlease choose an option:"
								+ "\n1. New Player"
									+ "\n2. Existing Player"
										+ "\n3. Guest Player (No Save)"
											+ "\n4. View Scoreboard"
												+ "\n5. Quit"
							+ "\n*******************************";
		
		int minOption = 1;
		int maxOption = 5;
		
		if (firstTime) {
			System.out.println(message);
			firstTime = false;
		}

		
		int choice = Input.getOption(minOption, maxOption, options);
		switch (choice) {
			case 1: makeUser(); break;
			case 2: existingUser(); break;
			case 3: //GameSystem.guestPlayed = true;
					gameMenu(GameSystem.guestPlayer);
					break;
			case 4: scoreBoard();
					welcome();
					break;
			case 5: GameSystem.quit(); break;
			default: System.out.println("\nOoops Error\n"); welcome(); break;
		}
	
	}
	
	
	static void makeUser() {
		
		String message = "\n Make a new user.\n";
		System.out.println(message);
		
		Scanner input = Input.consoleReader;
		input.nextLine();		// Clear the scanner								
		System.out.print("\nPlease enter a name: ");
		String name = input.nextLine().trim();
		
		// Check if given name is an existing player & handle
		if (GameSystem.playerObjects.containsKey(name)) {
			System.out.println("\nUser already exists.");
			String options = "\nPlease choose\n1. Play as " +name+
								"\n2. Make a new user";
			int choice = Input.getOption(1, 2, options);
			
			switch (choice) {
				case 1: gameMenu(GameSystem.playerObjects.get(name));
						break;
				case 2: makeUser(); break;
				default: makeUser(); break;
			}	
		}
		else {
			Player player = new Player(name);
			gameMenu(player);
		}

	}
	
	
	static void existingUser() {

		String message = "\n Load an existing user.\n";
		System.out.println(message);
		
		Scanner input = Input.consoleReader;
		input.nextLine();		// Clear the scanner								
		System.out.print("\nPlease enter a name: ");
		String name = input.nextLine().trim();
		
		if (!GameSystem.playerObjects.containsKey(name)) {
			System.out.println("\nUser does not exist.");
			String options = "\nPlease choose\n1. Try again\n2. Make a new user";
			int choice = Input.getOption(1, 2, options);
			
			switch (choice) {
				case 1: existingUser(); break;
				case 2: makeUser(); break;
				default: existingUser(); break;
			}
		}
		else {
			gameMenu(GameSystem.playerObjects.get(name));
		}
	}
	
	
	static void gameMenu(User player) {

		String options = "\nPlease choose a game by number (0 to quit):\n"
				+ "1: Rock-Paper-Scissors\n2: Bank Craps\n3: Maths Challenge";
		
		System.out.println(player.welcomeMessage());

				
		int minOption = 0;
		int maxOption = 3;
		
		int choice = Input.getOption(minOption, maxOption, options);
		
		Game game = null;
		
		switch (choice) {
			case 1: System.out.println("\nGame "+choice+" chosen");
					Game.rest(250);
					System.out.println("\n...loading...");
					game = new RockPaperScissors(player);
					break;
			case 2: System.out.println("\nGame "+choice+" chosen");
					Game.rest(250);
					System.out.println("\n...loading...");
					game = new Dice(player);
					break;
			case 3: System.out.println("\nGame "+choice+" chosen");
					Game.rest(250);
					System.out.println("\n...loading...");
					game = new Maths(player);
					break;
			case 0: player.endSession();
					welcome();
					break;
			default: welcome(); break;
		}
		
		player.setPlayedThisSession();
		game.play();
		
	}
	

	static void scoreBoard() {

		boolean guest = GameSystem.guestPlayer.hasPlayedThisSession();
		boolean guestPrinted = false;
		String boardHeader = "\n**************** Scoreboard **************"
							+"\n******************************************\n"
							+String.format("%-32s%10s", "Player", "Score")
							+"\n******************************************";
		String boardFooter = "******************************************\n";

		// Sort the players ArrayList
		Collections.sort(GameSystem.players);
		Collections.reverse(GameSystem.players);
		
		System.out.println(boardHeader);
		
		if (guest) {
			for (Player p : GameSystem.players) {
				if (!(guestPrinted) && p.getTotal() < GameSystem.guestPlayer.getPoints()) {
					System.out.println(GameSystem.guestPlayer.toString());
					guestPrinted = true;
					System.out.println(p.toString());
				}
				else {
					System.out.println(p.toString());				
				}
			}
			
			if (!guestPrinted) {
				System.out.println(GameSystem.guestPlayer.toString());
			}		
		}
		else {
			for (Player p : GameSystem.players) {
				System.out.println(p.toString());
			}
		}
		
		System.out.println(boardFooter);
		
	}
	

	
}
