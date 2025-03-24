import time
from ollama import chat
from ollama import ChatResponse

class Simulation:
    def __init__(self, grid_size_x=10, grid_size_y=10):
        self.grid_size_x = grid_size_x
        self.grid_size_y = grid_size_y
        self.point = [grid_size_x // 2, grid_size_y // 2]  # Start in the middle of the grid
        self.grid = [[0 for _ in range(grid_size_y)] for _ in range(grid_size_x)]
        self.grid[self.point[1]][self.point[0]] = 1  # Note the order of indices

    def get_direction_from_model(self):
        # Convert the grid to a string representation
        grid_text = '\n'.join(' '.join(str(cell) for cell in row) for row in self.grid)
        
        prompt = f'''Here is the current grid:\n{grid_text}\n  
                    You are the 1 in the grid of 0s.
                    Respond with only the word "up" or "down" or "left" or "right" to move you.
                    Lower case only. 
                    Moving "up" decreases the y-coordinate.
                    Moving "down" increases the y-coordinate.
                    Moving "left" decreases the x-coordinate.
                    Moving "right" increases the x-coordinate.
                    I want you to stick to the middle of the grid please.'''
        print(f"Prompt to AI:\n{prompt}\n")  # Debug: Print the prompt
        response: ChatResponse = chat(model='llama3', messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        direction = response['message']['content']
        print(f"AI Response: {direction}")  # Debug: Print the AI's response
        return direction

    def move_point(self):
        # Get direction from the Ollama model
        direction = self.get_direction_from_model()
        print(f"Moving {direction}")
        if direction == 'up' and self.point[1] > 0:
            self.point[1] -= 1
        elif direction == 'down' and self.point[1] < self.grid_size_y - 1:
            self.point[1] += 1
        elif direction == 'left' and self.point[0] > 0:
            self.point[0] -= 1
        elif direction == 'right' and self.point[0] < self.grid_size_x - 1:
            self.point[0] += 1

    def print_grid(self):
        self.grid = [[0 for _ in range(self.grid_size_y)] for _ in range(self.grid_size_x)]
        self.grid[self.point[1]][self.point[0]] = 1  # Note the order of indices
        for row in self.grid:
            print(' '.join(str(cell) for cell in row))
        print("\n" + "-"*20 + "\n")

    def run(self, steps=100):
        for _ in range(steps):
            self.move_point()
            self.print_grid()
            time.sleep(0.1)  # Pause for a short time to visualize the movement

if __name__ == "__main__":
    sim = Simulation()
    sim.run(steps=1000)