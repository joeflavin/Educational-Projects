package Project;

class VIP extends Player {
		
	private final boolean vip = true;
	static final String welcomeMessage = "\nWelcome back to the GameSystem";
		
	VIP(String name, int points, int history) {
			super(name, points, history);
		}
	
	@Override
	String welcomeMessage() {
		return welcomeMessage + " " +getName()+ "!";
	}
		
	@Override
	boolean isVIP() {
			return this.vip;
		}
	
	@Override
	void endSession() {
		incrementPoints(getPoints() / 10);	// ~10% Bonus Points for VIPs
		super.endSession();
	}
	
	
	@Override
	public String toString() {
		return String.format("%-32s%10d", "*"+this.getName()+"*", this.getTotal());
	}
		
}
