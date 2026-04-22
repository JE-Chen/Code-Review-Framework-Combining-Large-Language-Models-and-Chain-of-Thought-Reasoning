Title: A Simple 2D Shooting Game using Pygame

Overview: This Python script creates a simple 2D shooting game where the player controls a rectangle that moves around the screen and shoots bullets to destroy moving enemies. The game ends when the player's health reaches zero.

Detailed Explanation:

1. **Initialization**:
   - `pygame.init()` initializes all imported pygame modules.
   - Screen dimensions (W, H) and caption set up.
   - Clock object (`CLOCK_THING`) for controlling the frame rate.
   - Player, enemy, and bullet dictionaries initialized.
   - Strange flags dictionary contains game state information like panic mode.
   - Font object for rendering text.

2. **Main Game Loop**:
   - `running` flag controls the main loop.
   - `spawn_timer` tracks when new enemies should be spawned.
   - `frame_counter` counts frames for various timed events.
   - Event handling checks for window close event.

3. **Player Movement**:
   - Arrow keys move the player within screen bounds.

4. **Bullet Firing**:
   - Spacebar fires bullets at random velocities from the player's position every 10th frame.

5. **Enemy Behavior**:
   - Enemies move towards the player based on their speed.
   - New enemies are spawned randomly within the screen.

6. **Collision Detection**:
   - Bullets and enemies collide if distance is less than 10 pixels.
   - On collision, enemy life decreases, and bullet is removed.
   - If an enemy's life drops to zero, it is removed, and the player scores a point.
   - Player loses health if too close to an enemy; panic mode activates briefly.

7. **Score and Health Management**:
   - Health increases by 3 points every 5 scored points.

8. **Rendering**:
   - Screen filled with black background.
   - Player represented as green rectangle.
   - Enemies shown as red circles.
   - Bullets displayed as yellow circles.
   - HUD displays HP, score, and panic status.

9. **End Condition**:
   - Game exits when player runs out of health.

Improvements:
- Use proper exception handling instead of bare `except`.
- Implement better collision detection logic.
- Add more sophisticated graphics and animations.
- Improve user interface elements.
- Consider adding sound effects and music.
- Refactor into modular functions/classes for better organization.

Example Usage:
Run the script directly to start the game. No additional arguments are required.