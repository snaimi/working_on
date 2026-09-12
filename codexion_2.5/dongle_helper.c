/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   dongle_helper.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: snaimi <snaimi@student.1337.ma>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/06 18:30:00 by snaimi            #+#    #+#             */
/*   Updated: 2026/09/12 00:26:40 by snaimi           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static void	enqueue_coder(t_coder *coder, t_dongle *first, t_dongle *second)
{
	long long	key;
	long long	seq;

	get_priority_keys(coder, &key, &seq);
	pthread_mutex_lock(&first->mutex);
	pthread_mutex_lock(&second->mutex);
	heap_push(&first->queue, coder, key, seq);
	heap_push(&second->queue, coder, key, seq);
	pthread_mutex_unlock(&second->mutex);
	pthread_mutex_unlock(&first->mutex);
}

static int	wait_for_dongles(t_coder *coder, t_dongle *f, t_dongle *s)
{
	while (1)
	{
		pthread_mutex_lock(&f->mutex);
		pthread_mutex_lock(&s->mutex);
		if (is_simulation_over(coder))
		{
			heap_remove(&f->queue, coder);
			heap_remove(&s->queue, coder);
			pthread_mutex_unlock(&s->mutex);
			pthread_mutex_unlock(&f->mutex);
			return (0);
		}
		if (try_grab_both(coder, f, s))
			return (1);
		pthread_mutex_unlock(&s->mutex);
		pthread_mutex_unlock(&f->mutex);
		usleep(200);
	}
}

int	take_dongles(t_coder *coder)
{
	t_dongle	*f;
	t_dongle	*s;

	f = coder->left_dongle;
	s = coder->right_dongle;
	if (f->id > s->id)
	{
		f = coder->right_dongle;
		s = coder->left_dongle;
	}
	if (f == s)
		return (handle_single_coder(coder, f));
	enqueue_coder(coder, f, s);
	return (wait_for_dongles(coder, f, s));
}
