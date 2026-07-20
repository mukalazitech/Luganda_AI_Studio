'use strict';

const PRIMARY = Object.freeze([
  Object.freeze({ label: 'Home', page: 'index', icon: 'home' }),
  Object.freeze({ label: 'Translate', page: 'translate', icon: 'translate' }),
  Object.freeze({ label: 'Learn', page: 'learn', icon: 'learn' }),
  Object.freeze({ label: 'Explore', page: 'explore', icon: 'explore' }),
]);

const TOOLS = Object.freeze([
  Object.freeze({ label: 'Search', page: 'search', icon: 'search' }),
  Object.freeze({ label: 'Chat', page: 'chat', icon: 'chat' }),
]);

const INTERNAL = Object.freeze(['reviews.html', 'admin.html']);

module.exports = { PRIMARY, TOOLS, INTERNAL };
