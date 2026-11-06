import assert from 'node:assert/strict';
import { test } from 'node:test';

delete process.env.IG_GRAPH_HOST;
const { graphHostFor } = await import('../lib/instagram.js');

test('Unified-login (EAA) tokens go to graph.facebook.com, IGAA tokens to graph.instagram.com', () => {
  assert.equal(graphHostFor('EAAYexampleSystemUserToken'), 'graph.facebook.com');
  assert.equal(graphHostFor('IGAAexampleInstagramToken'), 'graph.instagram.com');
});

test('IG_GRAPH_HOST overrides the automatic choice', () => {
  process.env.IG_GRAPH_HOST = 'https://graph.instagram.com/';
  assert.equal(graphHostFor('EAAYx'), 'graph.instagram.com');
  delete process.env.IG_GRAPH_HOST;
});
