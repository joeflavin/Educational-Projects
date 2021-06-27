package Project;

import java.util.Scanner;

class Maths extends Game {
	 
	private static final String name = "Maths Challenge";
	private boolean firstTime = true;
		
	Maths(User gamer) {
		this.gamer = gamer;
	}
	
	String getName() {
		return name;
	}
		
	void play() {
		
		String instructions = "\n****************Instructions****************"
								+ "\nChoose a mathematical operation & practice."
									+"\n(DON'T CHEAT!!)"
							+"\n*******************************************";
		
		String message = "\nChoose a challenge:\n1. Addition"
							+"\n2. Multiplication\n3. End Game";
		

		if (firstTime) {
			gameIntro(getName());
			System.out.println(instructions);
			firstTime = false;
		}
		
		boolean add = true;
		
		int choice = Input.getOption(1,3, message);
		
		switch (choice) {
		case 1: break;
		case 2: add = false; break;
		case 3: quit();	break;
		default: play(); break;
		}
		
		challenge(add);
			
	}

	private void challenge(boolean add) {

		Scanner input = Input.consoleReader; 
		int score = 0;
		int attempt = -1;
		int ans;
		int operand1;
		int operand2;
		
		for (int i=0; i<5; i++) {
			
			if (add) {
				operand1 =  getRandomNumber(49, 499);
				operand2 = getRandomNumber(49, 499);
				ans = operand1 + operand2;
				
				System.out.println("\nAdd: " +operand1+ " + " +operand2);
			}
			else {
				operand1 =  getRandomNumber(11, 49);
				operand2 = getRandomNumber(11, 30);
				ans = operand1 * operand2;
				
				System.out.println("\nAdd: " +operand1+ " x " +operand2);
			}		
				
			if (input.hasNextInt()) {
				attempt = input.nextInt();
			}
			else {
				input.next();
			}
			
			while (attempt < 0) {
				System.out.println("\nPlease enter a non-negative intger: ");
				if (input.hasNextInt()) {
					attempt = input.nextInt();
				}
				else {
					input.next();
				}
			}
			
			if (ans == attempt) {
				System.out.println("\nCorrect!");
				score++;				
			}
			else {
				System.out.println("\nSorry incorrect. Try Again");
			}
		}
		
		System.out.println("\nYou got " +score+ " correct!");
		if (add) incrementPoints(score * 25);
		else incrementPoints(score * 50);
		
		play();
		
	}
	
}
