// Call-graph fixture, JavaScript (ES module): an exported function, an arrow, a class with a private method, "$".
export function start() {
    $("#main");
    return helper(1);
}

const helper = (n) => n + 1;

function $(selector) {
    return selector;
}

class Panel {
    show() {
        this.#paint();
    }

    #paint() {
        return 0;
    }
}

const handlers = {
    click() {},
    key: function () {},
};
