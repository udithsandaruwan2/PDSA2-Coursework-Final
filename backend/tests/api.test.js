// tests/api.test.js
const fetch = require('node-fetch');

const BASE = 'http://127.0.0.1:5000/tic_tac_toe';
const sessionId = Date.now().toString();
const headers = { 'Content-Type': 'application/json' };

describe('TicTacToe API', () => {
  test('POST /start returns 200 & success message', async () => {
    const res = await fetch(`${BASE}/start`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        session_id: sessionId,
        player_name: 'Alice',
        algorithm: 'minimax',
      }),
    });
    expect(res.status).toBe(200);
    const json = await res.json();
    expect(json).toHaveProperty('message', 'Game started!');
  });

  test('POST /move updates the board', async () => {
    const res = await fetch(`${BASE}/move`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        session_id: sessionId,
        move: [0, 0],
        playerName: 'Alice',
        algorithm: 'minimax',
      }),
    });
    expect(res.status).toBe(200);
    const json = await res.json();
    expect(Array.isArray(json.board)).toBe(true);
    expect(json.board[0][0]).toBe(1);
  });

  test('POST /move with bad session returns 400', async () => {
    const res = await fetch(`${BASE}/move`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        session_id: 'nope',
        move: [0, 0],
        playerName: 'Bob',
        algorithm: 'minimax',
      }),
    });
    expect(res.status).toBe(400);
    const json = await res.json();
    expect(json).toHaveProperty('error');
  });
});
