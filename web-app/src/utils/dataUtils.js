/**
 * 扁平数据转树形结构
 * @param {Array} data - 原始扁平数据
 * @param {String} idKey - 节点ID字段名
 * @param {String} parentKey - 父节点ID字段名
 * @param {String} labelKey - 标签字段名（映射到label）
 * @returns {Array} 树形结构数据
 */
export function flatToTree(data, idKey = 'id', parentKey = 'parent_id', labelKey = 'name') {
	// 0. 先按 sort_order 升序排列（数值越小越靠前）
	const sortedData = [...data].sort((a, b) => {
		const sortA = a.sort_order || 0;
		const sortB = b.sort_order || 0;
		return sortA - sortB;
	});

	// 1. 构建节点映射表（快速查找节点）
	const nodeMap = new Map();
	// 2. 存储最终根节点
	const tree = [];

	// 初始化映射表，同时格式化节点（只保留id/label，初始化children）
	// data.forEach((item) => {
	sortedData.forEach((item) => {
		nodeMap.set(item[idKey], {
			id: item[idKey],
			label: item[labelKey],
			source: item, // 原始数据，用于编辑时回显
			children: [], // 初始化子节点数组
		});
	});
	console.log('nodeMap', nodeMap);

	// 3. 构建父子关系
	// data.forEach((item) => {
	sortedData.forEach((item) => {
		const currentNode = nodeMap.get(item[idKey]);
		const parentId = item[parentKey];

		if (parentId === null) {
			// 无父节点 → 根节点
			tree.push(currentNode);
		} else {
			// 有父节点 → 找到父节点并添加到children
			const parentNode = nodeMap.get(parentId);
			if (parentNode) {
				parentNode.children.push(currentNode);
			}
		}
	});
	console.log('tree', tree);

	return tree;
}
