// Drag-and-drop for workflow designer (SortableJS CDN, ROADMAP 5)
import Sortable from "https://cdn.jsdelivr.net/npm/sortablejs@1.15/+esm";
export function enableDragDrop(container, onReorder) {
  return Sortable.create(container, { animation: 150, onEnd: onReorder });
}
