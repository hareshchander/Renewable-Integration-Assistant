import gradio as gr
from scipy.optimize import linprog
import matplotlib.pyplot as plt

def optimize_dispatch(solar_max, wind_max, grid_max, load):
    # Cost vector: prioritize solar and wind (zero cost), grid cost = 5 (example)
    c = [0, 0, 5]

    # Inequality constraints: x_i <= max capacity
    A_ub = [
        [1, 0, 0],  # solar <= solar_max
        [0, 1, 0],  # wind <= wind_max
        [0, 0, 1],  # grid <= grid_max
    ]
    b_ub = [solar_max, wind_max, grid_max]

    # Equality constraint: total supply = load
    A_eq = [[1, 1, 1]]
    b_eq = [load]

    bounds = [(0, None), (0, None), (0, None)]

    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

    if res.success:
        solar, wind, grid = [round(x, 2) for x in res.x]
        dispatch = {"Solar Power": solar, "Wind Power": wind, "Grid Power": grid}

        plt.figure(figsize=(6, 4))
        plt.bar(dispatch.keys(), dispatch.values(), color=['orange', 'green', 'blue'])
        plt.title("Optimized Power Dispatch (MW)")
        plt.ylabel("Power (MW)")
        plt.ylim(0, max(solar_max, wind_max, grid_max, load) * 1.1)
        plt.grid(axis='y')
        plt.tight_layout()
        plt.savefig("dispatch_plot.png")
        plt.close()

        # Format output as string with units, avoid percentage display
        result_str = "\n".join([f"{k}: {v} MW" for k, v in dispatch.items()])
        return result_str, "dispatch_plot.png"
    else:
        return "Error: Optimization failed. Please check inputs.", None

inputs = [
    gr.Number(label="Solar Max Capacity (MW)", value=50, minimum=0),
    gr.Number(label="Wind Max Capacity (MW)", value=60, minimum=0),
    gr.Number(label="Grid Max Capacity (MW)", value=100, minimum=0),
    gr.Number(label="Load Demand (MW)", value=120, minimum=0),
]

outputs = [
    gr.Label(label="Optimized Dispatch (MW)"),
    gr.Image(type="filepath", label="Dispatch Visualization")
]

demo = gr.Interface(
    fn=optimize_dispatch,
    inputs=inputs,
    outputs=outputs,
    title="Renewable Integration Optimization Assistant",
    description="Input max capacities of renewable sources and grid, along with load demand, to get optimized power dispatch minimizing grid usage."
)

if __name__ == "__main__":
    demo.launch()
