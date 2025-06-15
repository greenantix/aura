
/**
 * Test JavaScript file for Aura analysis
 */

function calculateSum(numbers) {
    let sum = 0;
    for (let i = 0; i < numbers.length; i++) {
        sum += numbers[i];
    }
    return sum;
}

// Missing documentation
function processArray(arr) {
    if (arr.length > 0) {
        if (typeof arr[0] === 'number') {
            if (arr[0] > 0) {
                return arr.map(x => x * 2);
            } else {
                return arr.map(x => Math.abs(x));
            }
        } else {
            return [];
        }
    } else {
        return [];
    }
}

class Calculator {
    constructor() {
        this.result = 0;
    }
    
    add(x) {
        this.result += x;
        return this;
    }
    
    multiply(x) {
        this.result *= x;
        return this;
    }
    
    getResult() {
        return this.result;
    }
}
