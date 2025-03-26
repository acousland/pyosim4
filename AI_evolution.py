import time
from ollama import chat
from ollama import ChatResponse

class Simulation:
    def __init__(self, grid_size_x=10, grid_size_y=10):
        self.grid_size_x = grid_size_x
        self.grid_size_y = grid_size_y
        # Initialize three points
        self.point1 = [grid_size_x // 3, grid_size_y // 3]  # Point 1 starts in the top-left third
        self.point2 = [2 * grid_size_x // 3, grid_size_y // 3]  # Point 2 starts in the bottom-right third
        self.point3 = [grid_size_x // 2, 2 * grid_size_y // 3]  # Point 3 starts in the middle-bottom
        self.grid = [[0 for _ in range(grid_size_y)] for _ in range(grid_size_x)]
        self.point1_alive = True
        self.point2_alive = True
        self.point3_alive = True
        self.update_grid()

    def update_grid(self):
        # Clear the grid and update the positions of the three points
        self.grid = [[0 for _ in range(self.grid_size_y)] for _ in range(self.grid_size_x)]
        if self.point1_alive:
            self.grid[self.point1[1]][self.point1[0]] = 1  # Mark point 1
        if self.point2_alive:
            self.grid[self.point2[1]][self.point2[0]] = 2  # Mark point 2
        if self.point3_alive:
            self.grid[self.point3[1]][self.point3[0]] = 3  # Mark point 3

    def get_direction_from_model(self, point_number, model_name):
        # Convert the grid to a string representation
        grid_text = '\n'.join(' '.join(str(cell) for cell in row) for row in self.grid)
        
        prompt = f'''Here is the current grid:\n{grid_text}\n  
                    You are point {point_number} on the grid, marked as {point_number}.
                    Your task is to eliminate all other players (non-zero numbers that are not you).

                    Rules:
                    • Respond with only one word: "up", "down", "left", "right", or "shoot".
                    • Use lowercase only.
                    • No explanations or multiple actions.
                    • "up" = decrease y
                    • "down" = increase y
                    • "left" = decrease x
                    • "right" = increase x
                    • If another player is adjacent (up/down/left/right), respond "shoot" to eliminate.
                                        
                    grid:\n{grid_text}'''
        #print(f"Prompt to AI for Point {point_number}:\n{prompt}\n")  # Debug: Print the prompt
        response: ChatResponse = chat(model=model_name, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        direction = response['message']['content']
        print(f"AI Response for Point {point_number}: {direction}")  # Debug: Print the AI's response
        return direction

    def move_point(self, point, point_number, model_name):
        # Get direction from the Ollama model
        direction = self.get_direction_from_model(point_number, model_name)
        print(f"Moving Point {point_number} {direction}")
        
        # Check if the other points are adjacent
        other_points = [
            (self.point2, self.point2_alive) if point_number == 1 else (self.point1, self.point1_alive),
            (self.point3, self.point3_alive) if point_number != 3 else (self.point1, self.point1_alive),
        ]
        for other_point, other_alive in other_points:
            if direction == "shoot" and other_alive and abs(point[0] - other_point[0]) + abs(point[1] - other_point[1]) == 1:
                print(f"Point {point_number} shot another point!")
                if other_point == self.point1:
                    self.point1_alive = False
                elif other_point == self.point2:
                    self.point2_alive = False
                elif other_point == self.point3:
                    self.point3_alive = False
                return  # End the move if a shot is fired

        # Move the point with wrapping
        if direction == 'up':
            point[1] = (point[1] - 1) % self.grid_size_y
        elif direction == 'down':
            point[1] = (point[1] + 1) % self.grid_size_y
        elif direction == 'left':
            point[0] = (point[0] - 1) % self.grid_size_x
        elif direction == 'right':
            point[0] = (point[0] + 1) % self.grid_size_x

    def print_grid(self):
        self.update_grid()  # Update the grid with the latest positions
        for row in self.grid:
            print(' '.join(str(cell) for cell in row))
        print("\n" + "-"*20 + "\n")

    def run(self, steps=100):
        for _ in range(steps):
            if self.point1_alive:
                self.move_point(self.point1, 1, 'llama3')  # Use model 'llama3' for point 1
            if self.point2_alive:
                self.move_point(self.point2, 2, 'llama3')  # Use model 'llama3' for point 2
            if self.point3_alive:
                self.move_point(self.point3, 3, 'llama3')  # Use model 'llama3' for point 3
            
            self.print_grid()
            if not self.point1_alive or not self.point2_alive or not self.point3_alive:
                print("Game over!")
                break
            #time.sleep(0.1)  # Pause for a short time to visualize the movement

if __name__ == "__main__":
    sim = Simulation()
    sim.run(steps=1000)