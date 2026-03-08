import mermaid from 'mermaid';

async function test() {
    mermaid.initialize({ startOnLoad: false });
    const tests = [
        `graph TD\nA["Data"] -->|Split|  B["Training Set"]\nA -->|Split|  C["Testing Set"]`,
        `graph TD\nA[Sequence] -->|Tokenize| B[Token Embedding]`,
        `graph TD\nA[Sequence] -->|Tokenize| B[Token Embed...]`
    ];
    
    for (const t of tests) {
        try {
            await mermaid.parse(t);
            console.log("SUCCESS");
        } catch(e) {
            console.log("FAIL", e.message);
        }
    }
}
test();
