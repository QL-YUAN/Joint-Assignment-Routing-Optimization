import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
import numpy as np
from matplotlib.animation import FuncAnimation
import itertools
def chess_constraint_fun(initial_positions, piece_labels, target_positions,target_labels):
    ls_assign_const_pieces=[[] for _ in range(32)]
    ls_assign_const_targets=[[] for _ in range(32)]
    #print(ls_assign_const_pieces)
    for i, j in itertools.product(range(len(initial_positions)),range(len(target_positions))):
        if piece_labels[i]==target_labels[j]:
            ls_assign_const_pieces[i].append((i,j))
            ls_assign_const_targets[j].append((i,j))

    return ls_assign_const_pieces,ls_assign_const_targets

def chess_plot_fun(initial_positions, piece_labels, target_positions,target_labels):
    """
    Plot a chessboard with pieces at given positions.
    
    Parameters
    ----------
    initial_positions : np.ndarray, shape (32, 2)
        Array of (x, y) coordinates for each piece.
    piece_labels : list or np.ndarray
        List of 32 labels (e.g., "wk", "bp", ...), same order as positions.
    target_positions : np.ndarray, optional, shape (32, 2)
        If given, draws arrows from initial to target positions.
    """
    
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # --- Draw chessboard ---
    for i in range(8):
        for j in range(8):
            color = "#DDB88C" if (i + j) % 2 == 0 else "#A66D4F"
            square = patches.Rectangle((i/8, j/8), 1/8, 1/8, facecolor=color)
            ax.add_patch(square)
    
    # --- Plot pieces ---
    for (x, y), label in zip(initial_positions, piece_labels):
        color = 'white' if label.startswith('w') else 'black'
        piece_symbol = label[1].upper()
        
        txt = ax.text(
            x, y,
            piece_symbol,
            color=color,
            ha='center', va='center',
            fontsize=18,
            fontweight='bold'
        )
        # Add outline to make white text visible on light squares
        txt.set_path_effects([
            path_effects.withStroke(linewidth=2, foreground='black' if color == 'white' else 'white')
        ])

    for i, j in itertools.product(range(len(initial_positions)),range(len(target_positions))):
        if piece_labels[i]==target_labels[j]:
            x0, y0=initial_positions[i,:]
            x1, y1=target_positions[j,:]
            ax.arrow(
                x0, y0, x1 - x0, y1 - y0,
                color='gray', alpha=0.5, width=0.002,
                length_includes_head=True, head_width=0.02
            )

    # --- Format board ---
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks(np.linspace(1/16, 15/16, 8))
    ax.set_yticks(np.linspace(1/16, 15/16, 8))
    ax.set_xticklabels(list("abcdefgh"))
    ax.set_yticklabels(range(1, 9))
    ax.set_title("Chess Piece Positions", fontsize=14, pad=15)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.show()

def reconstruct_cycle(edges, start):
    """
    Given a list of edges (i, j) forming a cycle and a start node,
    reconstruct the ordered list of nodes in the cycle starting and ending at start.
    
    Parameters
    ----------
    edges : list of tuple[int, int]
        List of edges forming a cycle (order unknown).
    start : int
        The node where to start reconstructing the cycle.
        
    Returns
    -------
    cycle : list[int]
        Ordered list of nodes forming the cycle starting and ending at start.
    """
    # Build adjacency dictionary for quick lookup
    adjacency = {}
    for i, j in edges:
        adjacency.setdefault(i, []).append(j)
        adjacency.setdefault(j, []).append(i)
    
    cycle = [start]
    current = start
    prev = None
    
    while True:
        # Get neighbors of current
        neighbors = adjacency[current]
        
        # Choose the neighbor that is not the previous node
        next_node = neighbors[0] if neighbors[0] != prev else neighbors[1]
        
        # If next_node is start, cycle complete
        if next_node == start:
            cycle.append(start)
            break
        
        cycle.append(next_node)
        prev, current = current, next_node
    
    return cycle

def animate_chess_pieces(positions_sequence, piece_labels,arrow_sequence):
    """
    Animate chess pieces moving over positions_sequence.
    
    positions_sequence: list or array of shape (frames, 32, 2)
        Positions of all 32 pieces for each frame.
    piece_labels: list of length 32
        Piece labels (e.g. 'wp', 'bk', etc.)
    """
    fig, ax = plt.subplots(figsize=(6, 6))

    # Draw chessboard once
    for i in range(8):
        for j in range(8):
            color = "#DDB88C" if (i + j) % 2 == 0 else "#A66D4F"
            square = patches.Rectangle((i/8, j/8), 1/8, 1/8, facecolor=color)
            ax.add_patch(square)

    # Create text objects once, initially at first frame positions
    texts = []
    for (x, y), label in zip(positions_sequence[0], piece_labels):
        color = 'white' if label.startswith('w') else 'black'
        piece_symbol = label[1].upper()
        txt = ax.text(
            x, y,
            piece_symbol,
            color=color,
            ha='center', va='center',
            fontsize=18,
            fontweight='bold'
        )
        txt.set_path_effects([
            path_effects.withStroke(linewidth=2, foreground='black' if color == 'white' else 'white')
        ])
        
        texts.append(txt)
    


    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_aspect('equal')
    # Initialize arrow as None
    arrow = None    
    def update(frame):
        nonlocal arrow  # <--- needed if this function is inside another function
        if arrow == None:
            # create arrow for the first time
            arrow = ax.arrow(0, 0, 0, 0, width=0.00001, color='blue')
        if arrow is not None:
            # update arrow position (recreate it)
            arrow.remove()
            #pass
        aw=arrow_sequence[frame]

        x0,y0,x1,y1=aw
        arrow = ax.arrow(x0,y0,x1-x0,y1-y0,
            width=0.01, color='blue')        

        # Update each piece position for the given frame
        for txt, pos in zip(texts, positions_sequence[frame]):
            txt.set_position(pos)
   
            #plt.pause(0.05)  # 50 ms pause
        return [arrow, *texts]

    anim = FuncAnimation(fig, update, frames=len(positions_sequence), interval=500, blit=True)
    plt.show()
