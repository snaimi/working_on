/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   heap.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: snaimi <snaimi@student.1337.ma>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/06 18:00:00 by snaimi            #+#    #+#             */
/*   Updated: 2026/09/12 00:07:20 by snaimi           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

int	heap_init(t_heap *heap, int capacity)
{
	heap->data = malloc(sizeof(t_heap_node) * capacity);
	if (!heap->data)
		return (0);
	heap->capacity = capacity;
	heap->size = 0;
	return (1);
}

void	heap_destroy(t_heap *heap)
{
	if (heap->data)
		free(heap->data);
	heap->data = NULL;
	heap->size = 0;
}

static int	is_higher_priority(t_heap_node a, t_heap_node b)
{
	if (a.key != b.key)
		return (a.key < b.key);
	if (a.seq != b.seq)
		return (a.seq < b.seq);
	return (a.coder->id < b.coder->id);
}

int	heap_push(t_heap *heap, t_coder *coder, long long key, long long seq)
{
	int			i;
	int			parent;
	t_heap_node	node;

	if (heap->size >= heap->capacity)
		return (0);
	node.coder = coder;
	node.key = key;
	node.seq = seq;
	i = heap->size++;
	while (i > 0)
	{
		parent = (i - 1) / 2;
		if (is_higher_priority(heap->data[parent], node))
			break ;
		heap->data[i] = heap->data[parent];
		i = parent;
	}
	heap->data[i] = node;
	return (1);
}

t_coder	*heap_pop(t_heap *heap)
{
	t_coder		*ret;
	t_heap_node	last;
	int			i;
	int			child;

	if (heap->size == 0)
		return (NULL);
	ret = heap->data[0].coder;
	last = heap->data[--heap->size];
	i = 0;
	while ((i * 2 + 1) < heap->size)
	{
		child = i * 2 + 1;
		if (child + 1 < heap->size
			&& is_higher_priority(heap->data[child + 1], heap->data[child]))
			child++;
		if (is_higher_priority(last, heap->data[child]))
			break ;
		heap->data[i] = heap->data[child];
		i = child;
	}
	if (heap->size > 0)
		heap->data[i] = last;
	return (ret);
}
