/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   heap_peek.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: snaimi <snaimi@student.1337.ma>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/06 18:00:00 by snaimi            #+#    #+#             */
/*   Updated: 2026/09/11 23:45:54 by snaimi           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

t_coder	*heap_peek(t_heap *heap)
{
	if (heap->size == 0)
		return (NULL);
	return (heap->data[0].coder);
}

void	heap_remove(t_heap *heap, t_coder *coder)
{
	int	i;
	int	j;

	i = 0;
	while (i < heap->size)
	{
		if (heap->data[i].coder == coder)
		{
			j = i;
			while (j < heap->size - 1)
			{
				heap->data[j] = heap->data[j + 1];
				j++;
			}
			heap->size--;
			return ;
		}
		i++;
	}
}
