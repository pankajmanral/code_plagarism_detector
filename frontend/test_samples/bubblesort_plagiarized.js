const sortValues = (data) => {
    let size = data.length;
    for (let x = 0; x < size; x++) {
        let y = 0;
        while (y < size - x - 1) {
            if (data[y] > data[y + 1]) {
                // Swap using destructuring for a structural change
                [data[y], data[y + 1]] = [data[y + 1], data[y]];
            }
            y += 1;
        }
    }
    return data;
};

const items = [4, 2, 8, 1, 6];
console.log(sortValues(items));
