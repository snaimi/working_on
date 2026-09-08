/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   codexion.h                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: snaimi <snaimi@student.1337.ma>            +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/08/24 03:00:00 by norminette        #+#    #+#             */
/*   Updated: 2026/09/06 18:06:25 by snaimi           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef CODEXION_H
# define CODEXION_H

# include <stdio.h>
# include <stdlib.h>
# include <unistd.h>
# include <pthread.h>
# include <sys/time.h>

# define SCHEDULER_FIFO 0
# define SCHEDULER_EDF  1

typedef struct s_coder	t_coder;

typedef struct s_heap_node
{
	t_coder		*coder;
	long long	key;
	long long	seq;
}	t_heap_node;

typedef struct s_heap
{
	t_heap_node	*data;
	int			capacity;
	int			size;
}	t_heap;

typedef struct s_dongle
{
	int				id;
	int				in_use;
	long long		cooldown_until;
	pthread_mutex_t	mutex;
	pthread_cond_t	cond;
	t_heap			queue;
}	t_dongle;

typedef struct s_metrics
{
	int			number_of_coders;
	long long	time_to_burnout;
	long long	time_to_compile;
	long long	time_to_debug;
	long long	time_to_refactor;
	long long	dongle_cooldown;
	int			number_of_compiles_required;
	int			scheduler;
}	t_metrics;

struct s_coder
{
	int				id;
	pthread_t		thread;
	long long		last_compile_start;
	int				compiles_done;
	t_dongle		*left_dongle;
	t_dongle		*right_dongle;
	struct s_data	*data;
};

typedef struct s_data
{
	t_metrics		metrics;
	long long		start_time;
	int				simulation_over;
	long long		global_seq;
	pthread_mutex_t	state_mutex;
	pthread_mutex_t	write_mutex;
	pthread_t		monitor_thread;
	t_coder			*coders;
	t_dongle		*dongles;
}	t_data;

/* Priority Queue / Heap Operations (heap.c & heap_peek.c) */
int			heap_init(t_heap *heap, int capacity);
void		heap_destroy(t_heap *heap);
int			heap_push(t_heap *heap, t_coder *coder,
				long long key, long long seq);
t_coder		*heap_pop(t_heap *heap);
t_coder		*heap_peek(t_heap *heap);

/* Parsing (parsing.c) */
int			parse_arguments(int argc, char **argv, t_metrics *metrics);

/* Time & Logging (timing.c / routines.c) */
long long	get_time_ms(void);
void		precise_sleep(long long duration_ms, t_data *data);
void		log_status(t_coder *coder, const char *status);

/* Dongle Operations (dongle.c & dongle_acquire.c) */
void		init_dongles(t_data *data);
void		destroy_dongles(t_data *data);
int			acquire_one_dongle(t_coder *coder, t_dongle *dongle);
int			take_dongles(t_coder *coder);
void		release_dongles(t_coder *coder);

/* Routines & Threads (routines.c & monitor.c) */
void		*coder_routine(void *arg);
void		*monitor_routine(void *arg);

#endif