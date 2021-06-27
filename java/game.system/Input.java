package Project;

import java.util.Scanner;


class Input {
	
	static final Scanner consoleReader = new Scanner(System.in);

	// Method to get a numerical choice within an inclusive range 
	static int getOption(int minOption, int maxOption, String options) {
		int choice = -2;
		Scanner input = consoleReader;
		System.out.println(options);
		if (input.hasNextInt()) {
			choice = input.nextInt();	// Set Choice
		}
		else {
			input.next();			// Consume invalid input
		}
		
		while (choice < minOption || choice > maxOption) {
			System.out.print("Please enter a valid numerical option: ");
			if (input.hasNextInt()) {
				choice = input.nextInt();
			}
			else {
				input.next();	// Consume invalid input
			}
		}

		return choice;
	}

	
	static void closeSTDIN() {
		consoleReader.close();
	}

}
