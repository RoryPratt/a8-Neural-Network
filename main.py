from neural import *
import pandas as pd
import pickle
import os
from sklearn.model_selection import train_test_split

def normalize(vec):
    total = sum(vec)
    return [x / total if total else 0 for x in vec]

print("Loading Data...")

df = pd.read_pickle("data.pkl")

df = df.sample(frac=1).reset_index(drop=True)[:2000]

df["input"] = df["input"].apply(normalize)

X_train, X_test, y_train, y_test = train_test_split(df["input"], df["output"], test_size=0.2, random_state=42)

train_data: List[Tuple[list, list]] = list(zip(X_train, y_train))

print("Complete")

neural_net = NeuralNet(96, 64, 5)

print("Looking for previous model...")

if os.path.exists("model_weights.pkl"):
	print("Loading Previous Model...")

	with open("model_weights.pkl", "rb") as f:
		model_state = pickle.load(f)
		f.close()

	neural_net.ih_weights = model_state["ih_weights"]
	neural_net.ho_weights = model_state["ho_weights"]

	print("Complete")
else:
	print("No previous model found")

print("Training Neural Net...")

neural_net.train(train_data, iters=5000, print_interval=10)

model_state = {
    "ih_weights": neural_net.get_ih_weights(),
    "ho_weights": neural_net.get_ho_weights(),
}

with open("model_weights.pkl", "wb") as f:
    pickle.dump(model_state, f)

print("Complete")

print("Testing Neural Net")

results = neural_net.test(X_test)

correct = 0

for idx, result in enumerate(results):
	_, y = result

	y = [1 if i == y.index(max(y)) else 0 for i in range(len(y))]

	actual = list(y_test)

	correct += int(y==list(actual[idx]))


accuracy = correct / len(y_test)

print(f"Accuracy: {accuracy:.2%}")

print("Complete")