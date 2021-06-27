package Project;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

public class GameSystem {
	
	private static final File saveDir = new File(new File(System.getProperty("user.home")), ".gameSys");
	private static final File saveFile = new File(saveDir, "savefile.txt");
	
	static ArrayList<Player> players = new ArrayList<Player>();
	static Map<String, Player> playerObjects = new HashMap<String, Player>();
	// Create the Guest User instance
	static final User guestPlayer = new User();
	
	public static void main (String[] args) {
		
		// Create save file if it doesn't exist
		try {
			saveFile.getParentFile().mkdirs();
			saveFile.createNewFile();
		} catch (IOException ex) {
			ex.printStackTrace();
		}
		
		// Initialise the system
		initialise();
		// Open the menu
		Menu.welcome();
	}
	
	static void initialise() {
		
		// Load the save file & make player objects
		try {
			
			Scanner fileReader = new Scanner(saveFile);
			
			while (fileReader.hasNextLine()) {
				// Read the file line by line
				String line = fileReader.nextLine();
//				System.out.println("line: "+line);
				String[] array = line.split(";");
				
				// Parse Array 
				String name = array[0];
				int points = Integer.parseInt(array[1]);
				int history = Integer.parseInt(array[2]);
				boolean vip = Boolean.parseBoolean(array[3]);
				
				// Make Player Objects
				// Constructor adds them to arraylist & hashmap
				if (vip) new VIP(name, points, history);
				else new Player(name, points, history);
			}	
			
			fileReader.close();	
		} 
		catch (FileNotFoundException ex) {
			ex.printStackTrace();
		}
		
	}
	
	static void quit() {
		
		String output = "";
		
		for (Player p: players) {
			// If Player played increment attribute
			if (p.playedThisSession) p.incrementTimesPlayed();
			// Add Session Points to Total for each Player in players list
			p.endSession();
			// Append Player details to output string
			output += p.save();
		}
		
		try {
			// Overwrite to the save file with new data
			BufferedWriter writer = new BufferedWriter(new FileWriter(saveFile));
			writer.write(output);
			writer.close();	
		}
		catch (IOException ex) {
			ex.printStackTrace();
		}
		
		// call the Score-board
		Menu.scoreBoard();
		// Close the console scanner
		Input.closeSTDIN();

		System.out.println("\n*****Quiting... Good-bye*****");

		System.exit(0);
	}
	
	// Adds player objects to arraylist & hashmap as they are created
	static void addPlayer(Player player) {
		players.add(player);
		playerObjects.put(player.getName(), player);
	}
		
}
