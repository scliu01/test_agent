// 导入封装的axios对象
import request from '@/api/request.js';
// 请求模块名称，对应后面的名称
const module_name = 'document';

class DocumentApi {
	// 构造函数
	constructor() {}

	/**
	 * 查询所有数据
	 * @returns 返回所有数据
	 */
	queryAll(project_id) {
		// 注意下的是反引号，在ESC键下面那个键
		return request.get(`/${module_name}/queryAll?project_id=${project_id}`);
	}

	/**
	 * 插入数据
	 * @param {Object} form 插入的数据
	 * @returns 插入结果
	 */
	insert(form) {
		return request.post(`/${module_name}/insert`, form);
	}

	/**
	 * 根据id查询数据
	 * @param {String} id 查询的id
	 * @returns 查询结果
	 */
	queryById(id) {
		return request.get(`/${module_name}/queryById?id=${id}`);
	}

	/**
	 * 更新数据
	 * @param {Object} form 更新的数据
	 * @returns 更新结果
	 */
	update(form) {
		return request.put(`/${module_name}/update`, form);
	}

	/**
	 * 删除数据
	 * @param {String} id 删除的id
	 * @returns 删除结果
	 */
	deleteById(id) {
		return request.delete(`/${module_name}/delete?id=${id}`);
	}

	// 根据新的图片上传接口，上传图片
	importDocument(data) {
		return request.post(`/${module_name}/importDocument`, data);
	}

	/**
	 * 使用AI处理生成测试数据（流式响应）
	 * @param {*} data 包含生成配置的对象
	 * @param {*} options 包含回调函数和信号量的对象
	 * @returns
	 */
	processWithAIStream(data, options = {}) {
		// onMessage, onError, onComplete都是对应的处理函数，分别处理流数据、错误和完成的情况
		const { onMessage, onError, onComplete, signal } = options;

		// 手动添加Authorization token
		const headers = {
			'Content-Type': 'application/json',
		};
		const token = localStorage.getItem('access_token');
		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}
		return fetch(`/api/${module_name}/process_with_ai_stream`, {
			method: 'POST',
			headers,
			body: JSON.stringify(data),
			signal,
			// 关键：保持连接，不缓存响应
			cache: 'no-cache',
		}).then(async (response) => {
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			// 创建流读取器
			const reader = response.body.getReader();
			// 创建一个TextDecoder实例
			const decoder = new TextDecoder();
			// 拼接缓冲区，每一次流数据到来，就拼接到缓冲区
			let buffer = '';

			try {
				// 循环读取流中的数据，当done变量为true时，停止
				while (true) {
					const { value, done } = await reader.read();

					// 解码并添加到缓冲区
					const chunk = decoder.decode(value, { stream: true });
					buffer += chunk;

					// 按行分割处理完整的JSON对象
					const lines = buffer.split('\n');

					// 保留最后不完整的行（如果有）
					buffer = lines.pop() || '';

					// 处理完整的行
					for (const line of lines) {
						const trimmedLine = line.trim();
						if (!trimmedLine) continue;

						try {
							const data = JSON.parse(trimmedLine);
							// 处理数据的函数
							onMessage?.(data);
						} catch (e) {
							console.warn('解析JSON失败:', trimmedLine, e);
							// 如果是JSON解析错误，可能是数据不完整，放回缓冲区
							buffer = trimmedLine + '\n' + buffer;
						}
					}
					if (done) {
						// 处理最后可能剩余的数据
						if (buffer.trim()) {
							const lines = buffer.split('\n').filter((line) => line.trim());
							for (const line of lines) {
								try {
									const data = JSON.parse(line);
									onMessage?.(data);
								} catch (e) {
									console.warn('解析最后数据失败:', line, e);
								}
							}
						}
						// 当流完成时，调用onComplete函数
						onComplete?.();
						break;
					}
				}
			} catch (error) {
				// 当流发生错误时，调用onError函数
				onError?.(error);
				throw error;
			}
		});
	}
}

// 导出对象，不导出就无法被其它文件导入使用
export default new DocumentApi();
